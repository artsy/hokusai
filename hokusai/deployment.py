import os
import sys
import datetime
import json

from hokusai.command import command
from hokusai.config import HokusaiConfig
from hokusai.common import print_red, print_green, shout, select_context, kubernetes_object, get_ecr_login

class Deployment(object):
  def __init__(self, context):
    self.context = context
    self.config = HokusaiConfig().check()

  def update(self, tag):
    select_context(self.context)
    print_green("Deploying %s to %s" % (tag, self.context))

    if self.context != tag:
      shout(get_ecr_login(self.config.aws_account_id))

      shout("docker pull %s:%s" % (self.config.aws_ecr_registry, tag))

      shout("docker tag %s:%s %s:%s" % (self.config.aws_ecr_registry, tag, self.config.aws_ecr_registry, self.context))
      shout("docker push %s:%s" % (self.config.aws_ecr_registry, self.context))
      print_green("Updated tag %s:%s -> %s:%s" %
                  (self.config.aws_ecr_registry, tag, self.config.aws_ecr_registry, self.context))

      deployment_tag = "%s--%s" % (self.context, datetime.datetime.utcnow().strftime("%Y-%m-%d--%H-%M-%S"))
      shout("docker tag %s:%s %s:%s" % (self.config.aws_ecr_registry, tag, self.config.aws_ecr_registry, deployment_tag))
      shout("docker push %s:%s" % (self.config.aws_ecr_registry, deployment_tag))
      print_green("Updated tag %s:%s -> %s:%s"
                  % (self.config.aws_ecr_registry, tag, self.config.aws_ecr_registry, deployment_tag))

    deployments = kubernetes_object('deployment', selector="app=%s" % self.config.project_name)
    if len(deployments['items']) != 1:
      print_red("Multiple deployments found for %s" % self.config.project_name)
      return -1

    deployment = deployments['items'][0]
    containers = deployment['spec']['template']['spec']['containers']
    container_names = [container['name'] for container in containers]
    deployment_targets = [{"name": name, "image": "%s:%s" % (self.config.aws_ecr_registry, tag)} for name in container_names]
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
    shout("kubectl patch deployment %s -p '%s'" % (self.config.project_name, json.dumps(patch)))

  def get_current_tag(self):
    select_context(self.context)

    deployments = kubernetes_object('deployment', selector="app=%s" % self.config.project_name)
    if len(deployments['items']) != 1:
      print_red("Multiple deployments found for %s" % self.config.project_name)
      return None

    deployment = deployments['items'][0]
    containers = deployment['spec']['template']['spec']['containers']
    container_names = [container['name'] for container in containers]
    container_images = [container['image'] for container in containers]

    if not all(x == container_images[0] for x in container_images):
      print_red("Deployment's containers do not reference the same image tag")
      return None

    base_image = containers[0]['image']
    return base_image.rsplit(':', 1)[1]
