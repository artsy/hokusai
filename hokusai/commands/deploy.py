import sys
import datetime
import json

from hokusai.command import command
from hokusai.config import HokusaiConfig
from hokusai.common import print_green, shout, select_context, kubernetes_object, get_ecr_login

@command
def deploy(context, tag):
  config = HokusaiConfig().check()

  select_context(context)

  if context != tag:
    shout(get_ecr_login(config.aws_account_id))

    shout("docker pull %s:%s" % (config.aws_ecr_registry, tag))

    shout("docker tag %s:%s %s:%s" %
                     (config.aws_ecr_registry, tag, config.aws_ecr_registry, context))

    shout("docker push %s:%s" % (config.aws_ecr_registry, context))
    print_green("Updated tag %s:%s -> %s:%s" %
                (config.aws_ecr_registry, tag, config.aws_ecr_registry, context))

    deployment_tag = "%s--%s" % (context, datetime.datetime.utcnow().strftime("%Y-%m-%d--%H-%M-%S"))
    shout("docker tag %s:%s %s:%s"
                     % (config.aws_ecr_registry, tag, config.aws_ecr_registry, deployment_tag))
    shout("docker push %s:%s" % (config.aws_ecr_registry, deployment_tag))
    print_green("Updated tag %s:%s -> %s:%s"
                % (config.aws_ecr_registry, tag, config.aws_ecr_registry, deployment_tag))

  deployments = kubernetes_object('deployment', selector="app=%s" % config.project_name)
  if len(deployments['items']) != 1:
    print_red("Multiple deployments found for %s" % config.project_name)
    return -1

  deployment = deployments['items'][0]
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

  shout("kubectl patch deployment %s -p '%s'" % (config.project_name, json.dumps(patch)))
  print_green("Deployment updated to %s" % tag)
