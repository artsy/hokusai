import datetime
import json

from hokusai.lib.config import config
from hokusai.services.kubectl import Kubectl
from hokusai.services.ecr import ECR
from hokusai.lib.common import print_red, print_green, shout

class Deployment(object):
  def __init__(self, context):
    self.context = context
    self.kctl = Kubectl(self.context)
    self.cache = [i for l in [self.kctl.get_object('deployment', selector="app=%s" % d) for d in config.deployments] for i in l]

  def update(self, tag):
    print_green("Deploying %s to %s" % (tag, self.context))

    if self.context != tag:
      shout(ECR().get_login())

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

    deployment_timestamp = datetime.datetime.utcnow().strftime("%s%f")
    for deployment in self.cache:
      containers = deployment['spec']['template']['spec']['containers']
      container_names = [container['name'] for container in containers]
      deployment_targets = [{"name": name, "image": "%s:%s" % (config.aws_ecr_registry, tag)} for name in container_names]
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
      shout(self.kctl.command("patch deployment %s -p '%s'" % (config.project_name, json.dumps(patch))))

  @property
  def state(self):
    return self.cache

  @property
  def current_tag(self):
    images = []
    for deployment in self.cache:
      containers = deployment['spec']['template']['spec']['containers']
      container_names = [container['name'] for container in containers]
      container_images = [container['image'] for container in containers]
      if not all(x == container_images[0] for x in container_images):
        print_red("Deployment's containers do not reference the same image tag")
        return None
      images.append(containers[0]['image'])
    if not all(y == images[0] for y in images):
      print_red("Deployments do not reference the same image tag")
      return None
    return images[0].rsplit(':', 1)[1]
