import os

from hokusai.command import command
from hokusai.config import HokusaiConfig
from hokusai.common import print_green, shout

@command
def build():
  config = HokusaiConfig().check()
  docker_compose_yml = os.path.join(os.getcwd(), 'hokusai/common.yml')
  shout("docker-compose -f %s -p build build" % docker_compose_yml, print_output=True)
  print_green("Built build_%s:latest" % config.project_name)
