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
    self.cache = self.kctl.get_object('deployment', selector="app=%s,layer=application" % config.project_name)

  def update(self, tag):
    print_green("Deploying %s to %s..." % (tag, self.context))

    if self.context != tag:
      ecr = ECR()

      ecr.retag(tag, self.context)
      print_green("Updated tag %s -> %s" % (tag, self.context))

      deployment_tag = "%s--%s" % (self.context, datetime.datetime.utcnow().strftime("%Y-%m-%d--%H-%M-%S"))
      ecr.retag(tag, deployment_tag)
      print_green("Updated tag %s -> %s" % (tag, deployment_tag))

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
      print_green("Updating %s..." % deployment['metadata']['name'])
      shout(self.kctl.command("patch deployment %s -p '%s'" % (deployment['metadata']['name'], json.dumps(patch))))

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
        print_red("Deployment's containers do not reference the same image tag")
        return None
      images.append(containers[0]['image'])
    if not all(y == images[0] for y in images):
      print_red("Deployments do not reference the same image tag")
      return None
    return images[0].rsplit(':', 1)[1]
