from subprocess import check_call, CalledProcessError

from hokusai.config import HokusaiConfig
from hokusai.common import *

def images():
  config = HokusaiConfig().check()
  try:
    print('\n')
    print_green('REMOTE IMAGES')
    print_green('---------------------------')
    check_call("docker images %s" % config.aws_ecr_registry, shell=True)
    print('\n')
    print_green('LOCAL IMAGES')
    print_green('---------------------------')
    check_call("docker images build_%s" % config.project_name, shell=True)
    check_call("docker images ci_%s" % config.project_name, shell=True)
    print('\n')
  except CalledProcessError:
    return -1
  return 0
