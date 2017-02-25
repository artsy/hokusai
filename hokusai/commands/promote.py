import os
import datetime

from subprocess import check_output, check_call, CalledProcessError, STDOUT

from hokusai.config import HokusaiConfig
from hokusai.common import print_red, print_green, verbose, select_context, HokusaiCommandError, kubernetes_object

def promote(context, from_context):
  config = HokusaiConfig().check()

  try:
    select_context(from_context)
  except HokusaiCommandError, e:
    print_red(repr(e))
    return -1

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

  tag = base_image.split(':')[1]

  print_green("Deploying %s to %s" % (tag, context))

  try:
    select_context(context)
  except HokusaiCommandError, e:
    print_red(repr(e))
    return -1

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

  deployment_targets = ["%s=%s" % (name, "%s:%s" % (config.aws_ecr_registry, tag)) for name in container_names]

  try:
    check_call(verbose("kubectl set image deployment/%s %s" % (config.project_name, ' '.join(deployment_targets))), shell=True)
  except CalledProcessError, e:
    print_red("Promotion failed with error: %s" % e.output)
    return -1

  print_green("Promoted %s to %s from %s" % (context, tag, from_context))
  return 0
