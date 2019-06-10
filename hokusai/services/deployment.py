import os
import datetime
import json
from tempfile import NamedTemporaryFile

import yaml

from hokusai import CWD
from hokusai.lib.config import HOKUSAI_CONFIG_DIR, config
from hokusai.services.kubectl import Kubectl
from hokusai.services.ecr import ECR, ClientError
from hokusai.lib.common import print_green, print_red, print_yellow, shout, shout_concurrent
from hokusai.services.command_runner import CommandRunner
from hokusai.lib.exceptions import CalledProcessError, HokusaiError
from hokusai.lib.constants import YAML_HEADER

class Deployment(object):
  def __init__(self, context, deployment_name=None, namespace=None):
    self.context = context
    self.namespace = namespace
    self.kctl = Kubectl(self.context, namespace=namespace)
    self.ecr = ECR()
    if deployment_name:
      self.cache = [self.kctl.get_object("deployment %s" % deployment_name)]
    else:
      self.cache = self.kctl.get_objects('deployment', selector="app=%s,layer=application" % config.project_name)

  def update(self, tag, constraint, git_remote, timeout,
              resolve_tag_sha1=True, update_config=False, filename=None):
    if not self.ecr.project_repo_exists():
      raise HokusaiError("Project repo does not exist.  Aborting.")

    if resolve_tag_sha1:
      tag = self.ecr.find_git_sha1_image_tag(tag)
      if tag is None:
        raise HokusaiError("Could not find a git SHA1 for tag %s.  Aborting." % tag)

    if self.namespace is None:
      print_green("Deploying %s to %s..." % (tag, self.context), newline_after=True)
    else:
      print_green("Deploying %s to %s/%s..." % (tag, self.context, self.namespace), newline_after=True)

    if config.pre_deploy is not None:
      print_green("Running pre-deploy hook '%s'..." % config.pre_deploy, newline_after=True)
      return_code = CommandRunner(self.context, namespace=self.namespace).run(tag, config.pre_deploy, constraint=constraint, tty=False)
      if return_code:
        raise HokusaiError("Pre-deploy hook failed with return code %s" % return_code, return_code=return_code)

    deployment_timestamp = datetime.datetime.utcnow().strftime("%s%f")

    if update_config:
      if filename is None:
        kubernetes_yml = os.path.join(CWD, HOKUSAI_CONFIG_DIR, "%s.yml" % self.context)
      else:
        kubernetes_yml = filename

      print_green("Patching Deployments in spec %s with tag %s" % (kubernetes_yml, tag), newline_after=True)
      payload = []
      for item in yaml.safe_load_all(open(kubernetes_yml, 'r')):
        if item['kind'] == 'Deployment':
          item['spec']['template']['metadata']['labels']['deploymentTimestamp'] = deployment_timestamp
          item['spec']['progressDeadlineSeconds'] = timeout
          for container in item['spec']['template']['spec']['containers']:
            if self.ecr.project_repo in container['image']:
              container['image'] = "%s:%s" % (self.ecr.project_repo, tag)
        payload.append(item)

      f = NamedTemporaryFile(delete=False)
      f.write(YAML_HEADER)
      f.write(yaml.safe_dump_all(payload, default_flow_style=False))
      f.close()

      print_green("Applying patched spec %s..." % f.name, newline_after=True)
      try:
        shout(self.kctl.command("apply -f %s" % f.name), print_output=True)
      finally:
        os.unlink(f.name)

    else:
      for deployment in self.cache:
        containers = [(container['name'], container['image']) for container in deployment['spec']['template']['spec']['containers']]
        deployment_targets = [{"name": name, "image": "%s:%s" % (self.ecr.project_repo, tag)} for name, image in containers if self.ecr.project_repo in image]
        patch = {
          "spec": {
            "template": {
              "metadata": {
                "labels": {"deploymentTimestamp": deployment_timestamp}
              },
              "spec": {
                "containers": deployment_targets
              }
            },
            "progressDeadlineSeconds": timeout
          }
        }

        print_green("Patching deployment %s..." % deployment['metadata']['name'], newline_after=True)
        shout(self.kctl.command("patch deployment %s -p '%s'" % (deployment['metadata']['name'], json.dumps(patch))))

    print_green("Waiting for deployment rollouts to complete...")

    rollout_commands = [self.kctl.command("rollout status deployment/%s" % deployment['metadata']['name']) for deployment in self.cache]
    return_codes = shout_concurrent(rollout_commands, print_output=True)
    if any(return_codes):
      print_red("One or more deployment rollouts timed out!  Rolling back...", newline_before=True, newline_after=True)
      rollback_commands = [self.kctl.command("rollout undo deployment/%s" % deployment['metadata']['name']) for deployment in self.cache]
      shout_concurrent(rollback_commands, print_output=True)
      raise HokusaiError("Deployment failed!")

    post_deploy_success = True

    if config.post_deploy is not None:
      print_green("Running post-deploy hook '%s'..." % config.post_deploy, newline_after=True)
      return_code = CommandRunner(self.context, namespace=self.namespace).run(tag, config.post_deploy, constraint=constraint, tty=False)
      if return_code:
        print_yellow("WARNING: Running the post-deploy hook failed with return code %s" % return_code, newline_before=True, newline_after=True)
        print_yellow("The tag %s has been rolled out.  However, you should run the post-deploy hook '%s' manually, or re-run this deployment." % (tag, config.post_deploy), newline_after=True)
        post_deploy_success = False

    if self.namespace is None:
      deployment_tag = "%s--%s" % (self.context, datetime.datetime.utcnow().strftime("%Y-%m-%d--%H-%M-%S"))
      print_green("Updating ECR deployment tags in %s..." % self.ecr.project_repo, newline_after=True)
      try:
        self.ecr.retag(tag, self.context)
        print_green("Updated ECR tag %s -> %s" % (tag, self.context))

        self.ecr.retag(tag, deployment_tag)
        print_green("Updated ECR tag %s -> %s" % (tag, deployment_tag), newline_after=True)
      except (ValueError, ClientError) as e:
        print_yellow("WARNING: Updating ECR deployment tags failed due to the error: '%s'" % str(e), newline_before=True, newline_after=True)
        print_yellow("The tag %s has been rolled out.  However, you should create the ECR tags '%s' and '%s' manually, or re-run this deployment." % (tag, deployment_tag, self.context), newline_after=True)
        post_deploy_success = False

      remote = git_remote or config.git_remote
      if remote is not None:
        print_green("Pushing Git deployment tags to %s..." % remote, newline_after=True)
        try:
          shout("git fetch %s" % remote)
          shout("git tag -f %s %s" % (self.context, tag), print_output=True)
          shout("git tag -f %s %s" % (deployment_tag, tag), print_output=True)
          shout("git push -f --no-verify %s refs/tags/%s" % (remote, self.context), print_output=True)
          print_green("Updated Git tag %s -> %s" % (tag, self.context))
          shout("git push -f --no-verify %s refs/tags/%s" % (remote, deployment_tag), print_output=True)
          print_green("Updated Git tag %s -> %s" % (tag, deployment_tag), newline_after=True)
        except CalledProcessError as e:
          print_yellow("WARNING: Creating Git deployment tags failed due to the error: '%s'" % str(e), newline_before=True, newline_after=True)
          print_yellow("The tag %s has been rolled out.  However, you should create the Git tags '%s' and '%s' manually, or re-run this deployment." % (tag, deployment_tag, self.context), newline_after=True)
          post_deploy_success = False

    if post_deploy_success:
      print_green("Deployment succeeded!")
    else:
      raise HokusaiError("One or more post-deploy steps failed!")

  def refresh(self):
    deployment_timestamp = datetime.datetime.utcnow().strftime("%s%f")
    for deployment in self.cache:
      patch = {
        "spec": {
          "template": {
            "metadata": {
              "labels": {"deploymentTimestamp": deployment_timestamp}
            }
          }
        }
      }
      print_green("Refreshing %s..." % deployment['metadata']['name'], newline_after=True)
      shout(self.kctl.command("patch deployment %s -p '%s'" % (deployment['metadata']['name'], json.dumps(patch))))

    print_green("Waiting for refresh to complete...")

    rollout_commands = [self.kctl.command("rollout status deployment/%s" % deployment['metadata']['name']) for deployment in self.cache]
    return_codes = shout_concurrent(rollout_commands, print_output=True)
    if any(return_codes):
      raise HokusaiError("Refresh failed!")


  @property
  def names(self):
    return [deployment['metadata']['name'] for deployment in self.cache]

  @property
  def current_tag(self):
    images = []

    for deployment in self.cache:
      containers = deployment['spec']['template']['spec']['containers']
      container_images = [container['image'] for container in containers if self.ecr.project_repo in container['image']]

      if not container_images:
        raise HokusaiError("Deployment has no valid target containers.  Aborting.")
      if not all(x == container_images[0] for x in container_images):
        raise HokusaiError("Deployment's containers do not reference the same image tag.  Aborting.")

      images.append(container_images[0])

    if not all(y == images[0] for y in images):
      raise HokusaiError("Deployments do not reference the same image tag. Aborting.")

    return images[0].rsplit(':', 1)[1]
