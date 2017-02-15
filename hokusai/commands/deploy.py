import datetime

from subprocess import check_output, check_call, CalledProcessError, STDOUT

from hokusai.config import HokusaiConfig
from hokusai.common import *

def deploy(context, tag):
  config = HokusaiConfig().check()

  switch_context_result = check_output("kubectl config use-context %s" % context, stderr=STDOUT, shell=True)
  print_green("Switched context to %s" % context)
  if 'no context exists' in switch_context_result:
    print_red("Context %s does not exist.  Check ~/.kube/config" % context)
    return -1

  if context != tag:
    try:
      login_command = check_output("aws ecr get-login --region %s" % config.aws_ecr_region, shell=True)
      check_call(login_command, shell=True)

      check_call("docker tag %s:%s %s:%s" % (config.aws_ecr_registry, tag, config.aws_ecr_registry, context), shell=True)
      check_call("docker push %s:%s" % (config.aws_ecr_registry, context), shell=True)
      print_green("Updated tag %s:%s -> %s:%s" % (config.aws_ecr_registry, tag, config.aws_ecr_registry, context))

      deployment_tag = "%s--%s" % (context, datetime.datetime.utcnow().strftime("%Y-%m-%d--%H-%M-%S"))
      check_call("docker tag %s:%s %s:%s" % (config.aws_ecr_registry, tag, config.aws_ecr_registry, deployment_tag), shell=True)
      check_call("docker push %s:%s" % (config.aws_ecr_registry, deployment_tag), shell=True)
      print_green("Updated tag %s:%s -> %s:%s" % (config.aws_ecr_registry, tag, config.aws_ecr_registry, deployment_tag))

    except CalledProcessError:
      print_red('Failed to update tags')
      return -1

  try:
    check_call("kubectl set image deployment/%s %s=%s" % (config.project_name, config.project_name, "%s:%s" % (config.aws_ecr_registry, tag)), shell=True)
  except CalledProcessError:
    print_red('Deployment failed')
    return -1

  print_green("Deployment updated to %s" % tag)
  return 0
