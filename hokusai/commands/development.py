import os
import signal

from hokusai.command import command
from hokusai.config import HokusaiConfig
from hokusai.common import print_red, EXIT_SIGNALS, shout

@command
def development(skip_build):
  HokusaiConfig().check()
  docker_compose_yml = os.path.join(os.getcwd(), 'hokusai/development.yml')
  if not os.path.isfile(docker_compose_yml):
    print_red("Yaml file %s does not exist." % docker_compose_yml)
    return -1

  def cleanup(*args):
    pass
  for sig in EXIT_SIGNALS:
    signal.signal(sig, cleanup)

  if skip_build:
    opts = ''
  else:
    opts = '--build'
  shout("docker-compose -f %s up %s" % (docker_compose_yml, opts), print_output=True)
