import os
import signal

from hokusai.lib.command import command
from hokusai.lib.config import config
from hokusai.lib.common import print_red, print_green, shout, EXIT_SIGNALS, CalledProcessError

@command
def test(skip_build):
  docker_compose_yml = os.path.join(os.getcwd(), 'hokusai/test.yml')
  if not os.path.isfile(docker_compose_yml):
    print_red("Yaml file %s does not exist." % docker_compose_yml)
    return -1

  def cleanup(*args):
    shout("docker-compose -f %s -p hokusai stop" % docker_compose_yml)
    shout("docker-compose -f %s -p hokusai rm --force" % docker_compose_yml)
  for sig in EXIT_SIGNALS:
    signal.signal(sig, cleanup)

  opts = ' --abort-on-container-exit'
  if not skip_build:
    opts += ' --build'

  shout("docker-compose -f %s -p hokusai up%s" % (docker_compose_yml, opts), print_output=True)

  try:
    test_exit_code = int(shout("docker wait hokusai_%s_1" % config.project_name))
  except CalledProcessError:
    print_red('Docker wait failed.')
    shout("docker-compose -f %s -p hokusai stop" % docker_compose_yml)
    shout("docker-compose -f %s -p hokusai rm --force" % docker_compose_yml)
    return -1

  if test_exit_code != 0:
    print_red('Tests Failed - Exit Code: %s\n' % test_exit_code)
  else:
    print_green("Tests Passed")

  shout("docker-compose -f %s -p hokusai stop" % docker_compose_yml)
  shout("docker-compose -f %s -p hokusai rm --force" % docker_compose_yml)

  return test_exit_code
