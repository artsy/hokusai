import os

from hokusai.lib.command import command
from hokusai.lib.config import config
from hokusai.lib.common import print_red, shout

@command
def dev_start(skip_build, follow):
  docker_compose_yml = os.path.join(os.getcwd(), 'hokusai/development.yml')
  if not os.path.isfile(docker_compose_yml):
    print_red("Yaml file %s does not exist." % docker_compose_yml)
    return -1

  opts = ''
  if not skip_build:
    opts += ' --build'

  if follow:
    shout("docker-compose -f %s up%s" % (docker_compose_yml, opts), print_output=True)
  else:
    shout("docker-compose -f %s create%s" % (docker_compose_yml, opts), print_output=True)
    shout("docker-compose -f %s start" % docker_compose_yml, print_output=True)

@command
def dev_stop():
  docker_compose_yml = os.path.join(os.getcwd(), 'hokusai/development.yml')
  if not os.path.isfile(docker_compose_yml):
    print_red("Yaml file %s does not exist." % docker_compose_yml)
    return -1

  shout("docker-compose -f %s stop" % docker_compose_yml, print_output=True)

@command
def dev_status():
  docker_compose_yml = os.path.join(os.getcwd(), 'hokusai/development.yml')
  if not os.path.isfile(docker_compose_yml):
    print_red("Yaml file %s does not exist." % docker_compose_yml)
    return -1
  shout("docker-compose -f %s ps" % docker_compose_yml, print_output=True)

@command
def dev_logs(follow):
  docker_compose_yml = os.path.join(os.getcwd(), 'hokusai/development.yml')
  if not os.path.isfile(docker_compose_yml):
    print_red("Yaml file %s does not exist." % docker_compose_yml)
    return -1

  opts = ''
  if follow:
    opts += ' --follow'
  shout("docker-compose -f %s logs%s" % (docker_compose_yml, opts), print_output=True)

@command
def dev_shell():
  docker_compose_yml = os.path.join(os.getcwd(), 'hokusai/development.yml')
  if not os.path.isfile(docker_compose_yml):
    print_red("Yaml file %s does not exist." % docker_compose_yml)
    return -1
  shout("docker-compose -f %s exec %s sh" % (docker_compose_yml, config.project_name), print_output=True)

@command
def dev_clean():
  docker_compose_yml = os.path.join(os.getcwd(), 'hokusai/development.yml')
  if not os.path.isfile(docker_compose_yml):
    print_red("Yaml file %s does not exist." % docker_compose_yml)
    return -1
  shout("docker-compose -f %s stop" % docker_compose_yml, print_output=True)
  shout("docker-compose -f %s rm --force" % docker_compose_yml, print_output=True)
