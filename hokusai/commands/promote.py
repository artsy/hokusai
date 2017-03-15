import os
import sys
import datetime
import json

from hokusai.command import command
from hokusai.config import HokusaiConfig
from hokusai.common import print_red, print_green, shout, select_context, kubernetes_object, get_ecr_login

@command
def promote(from_context, context):
  config = HokusaiConfig().check()

  select_context(from_context)

  deployments = kubernetes_object('deployment', selector="app=%s" % config.project_name)
  if len(deployments['items']) != 1:
    print_red("Multiple deployments found for %s" % config.project_name)
    return -1

  deployment = deployments['items'][0]
  containers = deployment['spec']['template']['spec']['containers']
  container_names = [container['name'] for container in containers]
  container_images = [container['image'] for container in containers]

  if not all(x == container_images[0] for x in container_images):
    print_red("Deployment's containers do not reference the same image tag - aborting...")
    return -1

  base_image = containers[0]['image']
  if config.aws_ecr_registry not in base_image:
    print_red("Refusing to deploy unmanaged image %s - aborting..." % base_image)
    return -1

  tag = base_image.rsplit(':', 1)[1]

  print_green("Deploying %s to %s" % (tag, context))

  select_context(context)

  shout(get_ecr_login(config.aws_account_id))

  shout("docker pull %s:%s" % (config.aws_ecr_registry, tag))

  shout("docker tag %s:%s %s:%s" % (config.aws_ecr_registry, tag, config.aws_ecr_registry, context))
  shout("docker push %s:%s" % (config.aws_ecr_registry, context))
  print_green("Updated tag %s:%s -> %s:%s" %
              (config.aws_ecr_registry, tag, config.aws_ecr_registry, context))

  deployment_tag = "%s--%s" % (context, datetime.datetime.utcnow().strftime("%Y-%m-%d--%H-%M-%S"))
  shout("docker tag %s:%s %s:%s" % (config.aws_ecr_registry, tag, config.aws_ecr_registry, deployment_tag))
  shout("docker push %s:%s" % (config.aws_ecr_registry, deployment_tag))
  print_green("Updated tag %s:%s -> %s:%s"
              % (config.aws_ecr_registry, tag, config.aws_ecr_registry, deployment_tag))

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
  shout("kubectl patch deployment %s -p '%s'" % (config.project_name, json.dumps(patch)))
  print_green("Promoted %s to %s from %s" % (context, tag, from_context))
