import datetime
import json

from hokusai.lib.config import config
from hokusai.services.kubectl import Kubectl
from hokusai.services.ecr import ECR
from hokusai.lib.common import print_green, shout, shout_concurrent
from hokusai.services.command_runner import CommandRunner
from hokusai.lib.exceptions import HokusaiError

class Deployment(object):
  def __init__(self, context):
    self.context = context
    self.kctl = Kubectl(self.context)
    self.cache = self.kctl.get_object('deployment', selector="app=%s,layer=application" % config.project_name)

  def update(self, tag, constraint):
    print_green("Deploying %s to %s..." % (tag, self.context))

    if self.context != tag:
      ecr = ECR()

      ecr.retag(tag, self.context)
      print_green("Updated tag %s -> %s" % (tag, self.context))

      deployment_tag = "%s--%s" % (self.context, datetime.datetime.utcnow().strftime("%Y-%m-%d--%H-%M-%S"))
      ecr.retag(tag, deployment_tag)
      print_green("Updated tag %s -> %s" % (tag, deployment_tag))

    if config.pre_deploy is not None:
      print_green("Running pre-deploy hook '%s' on %s..." % (config.pre_deploy, self.context))
      return_code = CommandRunner(self.context).run(tag, config.pre_deploy, constraint=constraint)
      if return_code:
        raise HokusaiError("Pre-deploy hook failed with return code %s" % return_code, return_code=return_code)

    deployment_timestamp = datetime.datetime.utcnow().strftime("%s%f")
    for deployment in self.cache:
      containers = deployment['spec']['template']['spec']['containers']
      container_names = [container['name'] for container in containers]
      deployment_targets = [{"name": name, "image": "%s:%s" % (config.docker_repo, tag)} for name in container_names]
      patch = {
        "spec": {
          "template": {
            "metadata": {
              "labels": {"deploymentTimestamp": deployment_timestamp}
            },
            "spec": {
              "containers": deployment_targets
            }
          }
        }
      }
      print_green("Patching deployment %s..." % deployment['metadata']['name'])
      shout(self.kctl.command("patch deployment %s -p '%s'" % (deployment['metadata']['name'], json.dumps(patch))))

    print_green("Waiting for rollout to complete...")

    rollout_commands = [self.kctl.command("rollout status deployment/%s" % deployment['metadata']['name']) for deployment in self.cache]
    return_code = shout_concurrent(rollout_commands)
    if return_code:
      raise HokusaiError("Deployment failed!", return_code=return_code)

    if config.post_deploy is not None:
      print_green("Running post-deploy hook '%s' on %s..." % (config.post_deploy, self.context))
      return_code = CommandRunner(self.context).run(tag, config.post_deploy, constraint=constraint)
      if return_code:
        raise HokusaiError("Post-deploy hook failed with return code %s" % return_code, return_code=return_code)

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
      print_green("Refreshing %s..." % deployment['metadata']['name'])
      shout(self.kctl.command("patch deployment %s -p '%s'" % (deployment['metadata']['name'], json.dumps(patch))))

    print_green("Waiting for refresh to complete...")

    rollout_commands = [self.kctl.command("rollout status deployment/%s" % deployment['metadata']['name']) for deployment in self.cache]
    return_code = shout_concurrent(rollout_commands)
    if return_code:
      raise HokusaiError("Refresh failed!", return_code=return_code)

  def history(self, deployment_name):
    replicasets = self.kctl.get_object('replicaset', selector="app=%s,layer=application" % config.project_name)
    replicasets = filter(lambda rs: rs['metadata']['ownerReferences'][0]['name'] == deployment_name, replicasets)
    return sorted(replicasets, key=lambda rs: int(rs['metadata']['annotations']['deployment.kubernetes.io/revision']))

  @property
  def names(self):
    return [deployment['metadata']['name'] for deployment in self.cache]

  @property
  def current_tag(self):
    images = []

    for deployment in self.cache:
      containers = deployment['spec']['template']['spec']['containers']
      container_names = [container['name'] for container in containers]
      container_images = [container['image'] for container in containers]

      if not all(x == container_images[0] for x in container_images):
        raise HokusaiError("Deployment's containers do not reference the same image tag", return_code=return_code)

      images.append(containers[0]['image'])

    if not all(y == images[0] for y in images):
      raise HokusaiError("Deployments do not reference the same image tag", return_code=return_code)

    return images[0].rsplit(':', 1)[1]
