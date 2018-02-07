import os
import signal

from hokusai.lib.command import command
from hokusai.lib.config import config
from hokusai.lib.common import print_green, shout, EXIT_SIGNALS
from hokusai.lib.exceptions import HokusaiError

@command
def dev_start(build, detach):
  docker_compose_yml = os.path.join(os.getcwd(), 'hokusai/development.yml')
  if not os.path.isfile(docker_compose_yml):
    raise HokusaiError("Yaml file %s does not exist." % docker_compose_yml)

  def cleanup(*args):
    shout("docker-compose -f %s -p hokusai stop" % docker_compose_yml, print_output=True)
  for sig in EXIT_SIGNALS:
    signal.signal(sig, cleanup)

  opts = ''
  if build:
    opts += ' --build'
  if detach:
    opts += ' -d'

  if not detach:
    print_green("Starting development environment... Press Ctrl+C to stop.")

  shout("docker-compose -f %s -p hokusai up%s" % (docker_compose_yml, opts), print_output=True)

  if detach:
    print_green("Run `hokousai dev stop` to shut down, or `hokusai dev logs --follow` to tail output.")

@command
def dev_stop():
  docker_compose_yml = os.path.join(os.getcwd(), 'hokusai/development.yml')
  if not os.path.isfile(docker_compose_yml):
    raise HokusaiError("Yaml file %s does not exist." % docker_compose_yml)

  shout("docker-compose -f %s -p hokusai stop" % docker_compose_yml, print_output=True)

@command
def dev_status():
  docker_compose_yml = os.path.join(os.getcwd(), 'hokusai/development.yml')
  if not os.path.isfile(docker_compose_yml):
    raise HokusaiError("Yaml file %s does not exist." % docker_compose_yml)

  shout("docker-compose -f %s -p hokusai ps" % docker_compose_yml, print_output=True)

@command
def dev_logs(follow, tail):
  docker_compose_yml = os.path.join(os.getcwd(), 'hokusai/development.yml')
  if not os.path.isfile(docker_compose_yml):
    raise HokusaiError("Yaml file %s does not exist." % docker_compose_yml)

  opts = ''
  if follow:
    opts += ' --follow'
  if tail:
    opts += " --tail=%i" % tail

  shout("docker-compose -f %s -p hokusai logs%s" % (docker_compose_yml, opts), print_output=True)

@command
def dev_run(command, service_name, stop):
  docker_compose_yml = os.path.join(os.getcwd(), 'hokusai/development.yml')
  if not os.path.isfile(docker_compose_yml):
    raise HokusaiError("Yaml file %s does not exist." % docker_compose_yml)

  shout("docker-compose -f %s -p hokusai run %s %s" % (docker_compose_yml, service_name, command), print_output=True)

  if stop:
    shout("docker-compose -f %s -p hokusai stop" % docker_compose_yml, print_output=True)

@command
def dev_clean():
  docker_compose_yml = os.path.join(os.getcwd(), 'hokusai/development.yml')
  if not os.path.isfile(docker_compose_yml):
    raise HokusaiError("Yaml file %s does not exist." % docker_compose_yml)

  shout("docker-compose -f %s -p hokusai stop" % docker_compose_yml, print_output=True)
  shout("docker-compose -f %s -p hokusai rm --force" % docker_compose_yml, print_output=True)
