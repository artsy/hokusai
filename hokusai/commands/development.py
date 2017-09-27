import os
import signal

from hokusai.lib.command import command
from hokusai.lib.config import config
from hokusai.lib.common import print_red, shout, EXIT_SIGNALS

@command
def dev_start(build, detach):
  docker_compose_yml = os.path.join(os.getcwd(), 'hokusai/development.yml')
  if not os.path.isfile(docker_compose_yml):
    print_red("Yaml file %s does not exist." % docker_compose_yml)
    return -1

  def cleanup(*args):
    shout("docker-compose -f %s -p hokusai stop" % docker_compose_yml, print_output=True)
  for sig in EXIT_SIGNALS:
    signal.signal(sig, cleanup)

  opts = ''
  if build:
    opts += ' --build'
  if detach:
    opts += ' -d'

  shout("docker-compose -f %s -p hokusai up%s" % (docker_compose_yml, opts), print_output=True)

@command
def dev_stop():
  docker_compose_yml = os.path.join(os.getcwd(), 'hokusai/development.yml')
  if not os.path.isfile(docker_compose_yml):
    print_red("Yaml file %s does not exist." % docker_compose_yml)
    return -1

  shout("docker-compose -f %s -p hokusai stop" % docker_compose_yml, print_output=True)

@command
def dev_status():
  docker_compose_yml = os.path.join(os.getcwd(), 'hokusai/development.yml')
  if not os.path.isfile(docker_compose_yml):
    print_red("Yaml file %s does not exist." % docker_compose_yml)
    return -1
  shout("docker-compose -f %s -p hokusai ps" % docker_compose_yml, print_output=True)

@command
def dev_logs(follow):
  docker_compose_yml = os.path.join(os.getcwd(), 'hokusai/development.yml')
  if not os.path.isfile(docker_compose_yml):
    print_red("Yaml file %s does not exist." % docker_compose_yml)
    return -1

  opts = ''
  if follow:
    opts += ' --follow'
  shout("docker-compose -f %s -p hokusai logs%s" % (docker_compose_yml, opts), print_output=True)

@command
def dev_shell():
  docker_compose_yml = os.path.join(os.getcwd(), 'hokusai/development.yml')
  if not os.path.isfile(docker_compose_yml):
    print_red("Yaml file %s does not exist." % docker_compose_yml)
    return -1
  shout("docker-compose -f %s -p hokusai exec %s sh" % (docker_compose_yml, config.project_name), print_output=True)

@command
def dev_clean():
  docker_compose_yml = os.path.join(os.getcwd(), 'hokusai/development.yml')
  if not os.path.isfile(docker_compose_yml):
    print_red("Yaml file %s does not exist." % docker_compose_yml)
    return -1
  shout("docker-compose -f %s -p hokusai stop" % docker_compose_yml, print_output=True)
  shout("docker-compose -f %s -p hokusai rm --force" % docker_compose_yml, print_output=True)
