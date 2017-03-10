from subprocess import check_output, check_call, CalledProcessError

from hokusai.config import HokusaiConfig
from hokusai.common import print_red, print_green, get_ecr_login

def push(tag, test_build):
  config = HokusaiConfig().check()

  login_command = get_ecr_login(config.aws_account_id)
  if login_command is None:
    return -1

  try:
    check_call(login_command, shell=True)

    if test_build:
      build = "ci_%s:latest" % config.project_name
    else:
      build = "build_%s:latest" % config.project_name

    check_call("docker tag %s %s:%s" % (build, config.aws_ecr_registry, tag), shell=True)
    check_call("docker push %s:%s" % (config.aws_ecr_registry, tag), shell=True)
    print_green("Pushed %s to %s:%s" % (build, config.aws_ecr_registry, tag))

  except CalledProcessError:
    print_red('Push failed')
    return -1

  return 0
