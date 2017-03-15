from hokusai.command import command
from hokusai.config import HokusaiConfig
from hokusai.common import print_red, print_green, shout, get_ecr_login

@command
def pull():
  config = HokusaiConfig().check()
  shout(get_ecr_login(config.aws_account_id))
  print_green("Pulling from %s..." % config.aws_ecr_registry)
  shout("docker pull %s --all-tags" % config.aws_ecr_registry)
