from subprocess import check_output, check_call, CalledProcessError

from hokusai.config import HokusaiConfig
from hokusai.common import print_red, print_green, verbose, get_ecr_login

def pull():
  config = HokusaiConfig().check()

  login_command = get_ecr_login(config.aws_account_id)
  if login_command is None:
    return -1

  try:
    check_call(verbose(login_command), shell=True)
    print_green("Pulling from %s..." % config.aws_ecr_registry)
    check_output(verbose("docker pull %s --all-tags" % config.aws_ecr_registry), shell=True)
    print_green("Pull succeeded")
  except CalledProcessError:
    print_red('Pull failed')
    return -1
  return 0
