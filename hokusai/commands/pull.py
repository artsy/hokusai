from subprocess import check_output, check_call, CalledProcessError

from hokusai.config import HokusaiConfig
from hokusai.common import *

def pull():
  config = HokusaiConfig().check()

  try:
    login_command = check_output("aws ecr get-login --region %s" % config.aws_ecr_region, shell=True)
    check_call(login_command, shell=True)

    print("Pulling from %s..." % config.aws_ecr_registry)
    check_output("docker pull %s --all-tags" % config.aws_ecr_registry, shell=True)
    print_green("Pulled succeeded")
  except CalledProcessError:
    print_red('Pull failed')
    return -1
  return 0
