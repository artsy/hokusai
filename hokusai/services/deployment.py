import os
import datetime
import json
from tempfile import NamedTemporaryFile
import time

import yaml

from hokusai import CWD
from hokusai.lib.config import HOKUSAI_CONFIG_DIR, HOKUSAI_TMP_DIR, config
from hokusai.services.kubectl import Kubectl
from hokusai.services.ecr import ECR, ClientError
from hokusai.lib.common import print_green, print_red, print_yellow, shout, shout_concurrent
from hokusai.services.command_runner import CommandRunner
from hokusai.services.yaml_spec import YamlSpec
from hokusai.lib.exceptions import CalledProcessError, HokusaiError
from hokusai.lib.constants import YAML_HEADER
from hokusai.lib.template_selector import TemplateSelector

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

  def update(self, tag, constraint, git_remote, timeout, update_config=False, filename=None):
    if not self.ecr.project_repo_exists():
      raise HokusaiError("Project repo does not exist.  Aborting.")

    digest = self.ecr.image_digest_for_tag(tag)
    if digest is None:
      raise HokusaiError("Could not find an image digest for tag %s.  Aborting." % tag)

    if self.namespace is None:
      print_green("Deploying %s to %s..." % (digest, self.context), newline_after=True)
    else:
      print_green("Deploying %s to %s/%s..." % (digest, self.context, self.namespace), newline_after=True)

    """
    This logic should be refactored, but essentially if namespace and filename are provided, the caller is
    a review app, while if namespace is None it is either staging or production.  If filename is unset for staging
    or production it is targeting the 'canonical' app, i.e. staging.yml or production.yml while if it is set it is
    trageting a 'canary' app.

    For the canonical app, run deploy hooks and post-depoy steps creating deployment tags
    For a canary app, skip deploy hooks and post-deploy steps
    For review apps, run deploy hooks but skip post-deploy steps

    For all deployment rollouts, if update_config or filename targets a yml file, bust the
    deployment cache using k8s field selectors and get deployments to watch the rollout from
    the yml file spec
    """

    # Run the pre-deploy hook for the canonical app or a review app
    if config.pre_deploy and (filename is None or (filename and self.namespace)):
      print_green("Running pre-deploy hook '%s'..." % config.pre_deploy, newline_after=True)
      return_code = CommandRunner(self.context, namespace=self.namespace).run(digest, config.pre_deploy, constraint=constraint, tty=False)
      if return_code:
        raise HokusaiError("Pre-deploy hook failed with return code %s" % return_code, return_code=return_code)

    if filename is None:
      yaml_template = TemplateSelector().get(os.path.join(CWD, HOKUSAI_CONFIG_DIR, self.context))
    else:
      yaml_template = TemplateSelector().get(filename)

    yaml_spec = YamlSpec(yaml_template).to_list()

    # If a review app, a canary app or the canonical app while updating config,
    # bust the deployment cache and populate deployments from the yaml file
    if filename or update_config:
      self.cache = []
      for item in yaml_spec:
        if item['kind'] == 'Deployment':
          self.cache.append(item)

    # If updating config, patch the spec and apply
    if update_config:
      print_green("Patching Deployments in spec %s with image digest %s" % (yaml_template, digest), newline_after=True)
      payload = []
      for item in yaml_spec:
        if item['kind'] == 'Deployment':
          item['spec']['progressDeadlineSeconds'] = timeout
          for container in item['spec']['template']['spec']['containers']:
            if self.ecr.project_repo in container['image']:
              container['image'] = "%s@%s" % (self.ecr.project_repo, digest)
        payload.append(item)

      f = NamedTemporaryFile(delete=False, dir=HOKUSAI_TMP_DIR, mode='w')
      f.write(YAML_HEADER)
      f.write(yaml.safe_dump_all(payload, default_flow_style=False))
      f.close()

      print_green("Applying patched spec %s..." % f.name, newline_after=True)
      try:
        shout(self.kctl.command("apply -f %s" % f.name), print_output=True)
      finally:
        os.unlink(f.name)

    # If not updating config, patch the deployments in the cache and call kubectl patch to update
    else:
      for deployment in self.cache:
        containers = [(container['name'], container['image']) for container in deployment['spec']['template']['spec']['containers']]
        deployment_targets = [{"name": name, "image": "%s@%s" % (self.ecr.project_repo, digest)} for name, image in containers if self.ecr.project_repo in image]
        patch = {
          "spec": {
            "template": {
              "spec": {
                "containers": deployment_targets
              }
            },
            "progressDeadlineSeconds": timeout
          }
        }

        print_green("Patching deployment %s..." % deployment['metadata']['name'], newline_after=True)
        shout(self.kctl.command("patch deployment %s -p '%s'" % (deployment['metadata']['name'], json.dumps(patch))))

    # Watch the rollouts in the cache and if any fail, roll back
    print_green("Waiting for deployment rollouts to complete...")
    rollout_commands = [self.kctl.command("rollout status deployment/%s" % deployment['metadata']['name']) for deployment in self.cache]
    return_codes = shout_concurrent(rollout_commands, print_output=True)
    if any(return_codes):
      print_red("One or more deployment rollouts failed!  Rolling back...", newline_before=True, newline_after=True)
      rollback_commands = [self.kctl.command("rollout undo deployment/%s" % deployment['metadata']['name']) for deployment in self.cache]
      shout_concurrent(rollback_commands, print_output=True)
      raise HokusaiError("Deployment failed!")

    post_deploy_success = True

    # Run the post-deploy hook for the canonical app or a review app
    if config.post_deploy and (filename is None or (filename and self.namespace)):
      print_green("Running post-deploy hook '%s'..." % config.post_deploy, newline_after=True)
      return_code = CommandRunner(self.context, namespace=self.namespace).run(digest, config.post_deploy, constraint=constraint, tty=False)
      if return_code:
        print_yellow("WARNING: Running the post-deploy hook failed with return code %s" % return_code, newline_before=True, newline_after=True)
        print_yellow("The image digest %s has been rolled out.  However, you should run the post-deploy hook '%s' manually, or re-run this deployment." % (digest, config.post_deploy), newline_after=True)
        post_deploy_success = False

    # For the canonical app, create tags
    if filename is None:
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
      if remote:
        # Update git tags. Try up to 3 times, at 3 second intervals. Failure does not fail deployment.
        git_tag_sucess = False
        attempts = 0
        while ((not git_tag_sucess) and (attempts < 3)):
          try:
            attempts += 1
            print_green("Creating Git deployment tags '%s', '%s', and pushing them to %s..." % (self.context, deployment_tag, remote))
            print_green("Attempt# %s." % attempts)
            shout("git fetch -f %s --tags" % remote)
            shout("git tag -f %s %s" % (self.context, tag), print_output=True)
            shout("git tag -f %s %s" % (deployment_tag, tag), print_output=True)
            shout("git push -f --no-verify %s refs/tags/%s" % (remote, self.context), print_output=True)
            print_green("Updated Git tag %s -> %s" % (tag, self.context))
            shout("git push -f --no-verify %s refs/tags/%s" % (remote, deployment_tag), print_output=True)
            print_green("Updated Git tag %s -> %s" % (tag, deployment_tag), newline_after=True)
            git_tag_sucess = True
          except CalledProcessError as e:
            # If subprocess.check_output() was called, the actual error is in CalledProcessError's 'output' attribute.
            print_yellow("WARNING: Creating Git deployment tags failed due to the error:", newline_before=True, newline_after=True)
            print_yellow(e.output)
            time.sleep(3)

        if (not git_tag_sucess):
            print_yellow("Failed all attempts at pushing Git deployment tags! Please do it manually.", newline_after=True)

    if post_deploy_success:
      print_green("Deployment succeeded!")
    else:
      raise HokusaiError("One or more post-deploy steps failed!")

  def refresh(self):
    for deployment in self.cache:
      print_green("Refreshing %s..." % deployment['metadata']['name'], newline_after=True)
      shout(self.kctl.command("rollout restart deployment/%s" % deployment['metadata']['name']))

    print_green("Waiting for refresh to complete...")

    rollout_commands = [self.kctl.command("rollout status deployment/%s" % deployment['metadata']['name']) for deployment in self.cache]
    return_codes = shout_concurrent(rollout_commands, print_output=True)
    if any(return_codes):
      raise HokusaiError("Refresh failed!")


  @property
  def names(self):
    return [deployment['metadata']['name'] for deployment in self.cache]
