from hokusai.command import command
from hokusai.config import HokusaiConfig
from hokusai.common import print_green, shout

@command
def images():
  config = HokusaiConfig().check()
  print('\n')
  print_green('REMOTE IMAGES')
  print_green('---------------------------')
  shout("docker images %s" % config.aws_ecr_registry, print_output=True)
  print('\n')
  print_green('LOCAL IMAGES')
  print_green('---------------------------')
  shout("docker images build_%s" % config.project_name, print_output=True)
  shout("docker images ci_%s" % config.project_name, print_output=True)
  print('\n')
