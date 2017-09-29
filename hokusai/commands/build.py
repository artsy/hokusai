import os

from hokusai.lib.command import command
from hokusai.lib.config import config
from hokusai.lib.common import shout
from hokusai.lib.exceptions import HokusaiError

@command
def build():
  docker_compose_yml = os.path.join(os.getcwd(), 'hokusai/common.yml')
  if not os.path.isfile(docker_compose_yml):
    raise HokusaiError("Yaml file %s does not exist." % docker_compose_yml)
  shout("docker-compose -f %s -p hokusai build" % docker_compose_yml, print_output=True)
