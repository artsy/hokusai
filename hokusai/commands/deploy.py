import datetime
import json

from subprocess import check_output, check_call, CalledProcessError, STDOUT

from hokusai.config import HokusaiConfig
from hokusai.common import print_red, print_green, verbose, select_context, HokusaiCommandError, kubernetes_object

def deploy(context, tag):
  config = HokusaiConfig().check()

  try:
    select_context(context)
  except HokusaiCommandError, e:
    print_red(repr(e))
    return -1

  if context != tag:
    try:
      login_command = check_output(verbose("aws ecr get-login --region %s" % config.aws_ecr_region), shell=True)
      check_call(login_command, shell=True)

      check_call(verbose("docker pull %s:%s" % (config.aws_ecr_registry, tag)), shell=True)

      check_call(verbose("docker tag %s:%s %s:%s" %
                       (config.aws_ecr_registry, tag, config.aws_ecr_registry, context)), shell=True)
      check_call(verbose("docker push %s:%s" % (config.aws_ecr_registry, context)), shell=True)
      print_green("Updated tag %s:%s -> %s:%s" %
                  (config.aws_ecr_registry, tag, config.aws_ecr_registry, context))

      deployment_tag = "%s--%s" % (context, datetime.datetime.utcnow().strftime("%Y-%m-%d--%H-%M-%S"))
      check_call(verbose("docker tag %s:%s %s:%s"
                       % (config.aws_ecr_registry, tag, config.aws_ecr_registry, deployment_tag)), shell=True)
      check_call(verbose("docker push %s:%s" % (config.aws_ecr_registry, deployment_tag)), shell=True)
      print_green("Updated tag %s:%s -> %s:%s"
                  % (config.aws_ecr_registry, tag, config.aws_ecr_registry, deployment_tag))
    except CalledProcessError, e:
      print_red("Updating tags failed with error: %s" % e.output)
      return -1


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

  try:
    check_call(verbose("kubectl patch deployment %s -p '%s'" % (config.project_name, json.dumps(patch))), shell=True)
  except CalledProcessError, e:
    print_red("Deployment failed with error: %s" % e.output)
    return -1

  print_green("Deployment updated to %s" % tag)
  return 0
