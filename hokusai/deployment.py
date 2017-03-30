import datetime
import json

from hokusai.config import config
from hokusai.kubectl import Kubectl
from hokusai.common import print_red, print_green, shout, get_ecr_login

class Deployment(object):
  def __init__(self, context):
    self.context = context
    self.kctl = Kubectl(self.context)
    self.cache = self.kctl.get_object('deployment', selector="app=%s" % config.project_name)

  def update(self, tag):
    print_green("Deploying %s to %s" % (tag, self.context))

    if self.context != tag:
      shout(get_ecr_login(config.aws_account_id))

      shout("docker pull %s:%s" % (config.aws_ecr_registry, tag))

      shout("docker tag %s:%s %s:%s" % (config.aws_ecr_registry, tag, config.aws_ecr_registry, self.context))
      shout("docker push %s:%s" % (config.aws_ecr_registry, self.context))
      print_green("Updated tag %s:%s -> %s:%s" %
                  (config.aws_ecr_registry, tag, config.aws_ecr_registry, self.context))

      deployment_tag = "%s--%s" % (self.context, datetime.datetime.utcnow().strftime("%Y-%m-%d--%H-%M-%S"))
      shout("docker tag %s:%s %s:%s" % (config.aws_ecr_registry, tag, config.aws_ecr_registry, deployment_tag))
      shout("docker push %s:%s" % (config.aws_ecr_registry, deployment_tag))
      print_green("Updated tag %s:%s -> %s:%s"
                  % (config.aws_ecr_registry, tag, config.aws_ecr_registry, deployment_tag))

    if len(self.cache['items']) != 1:
      print_red("Multiple deployments found for %s" % config.project_name)
      return None

    deployment = self.cache['items'][0]
    containers = deployment['spec']['template']['spec']['containers']
    container_names = [container['name'] for container in containers]
    deployment_targets = [{"name": name, "image": "%s:%s" % (config.aws_ecr_registry, tag)} for name in container_names]
    patch = {
      "spec": {
        "template": {
          "metadata": {
            "labels": {"deploymentTimestamp": datetime.datetime.utcnow().strftime("%s%f")}
          },
          "spec": {
            "containers": deployment_targets
          }
        }
      }
    }
    shout(self.kctl.command("patch deployment %s -p '%s'" % (config.project_name, json.dumps(patch))))

  @property
  def state(self):
    if len(self.cache['items']) != 1:
      print_red("Multiple deployments found for %s" % config.project_name)
      return None
    return self.cache['items'][0]

  @property
  def current_tag(self):
    deployment = self.state
    if deployment is None:
      return None

    containers = deployment['spec']['template']['spec']['containers']
    container_names = [container['name'] for container in containers]
    container_images = [container['image'] for container in containers]

    if not all(x == container_images[0] for x in container_images):
      print_red("Deployment's containers do not reference the same image tag")
      return None

    base_image = containers[0]['image']
    return base_image.rsplit(':', 1)[1]
