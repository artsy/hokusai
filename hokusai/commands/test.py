import os
import signal

from hokusai.lib.command import command
from hokusai.lib.config import config
from hokusai.lib.common import print_red, print_green, shout, EXIT_SIGNALS, CalledProcessError

@command
def test():
  docker_compose_yml = os.path.join(os.getcwd(), 'hokusai/test.yml')
  if not os.path.isfile(docker_compose_yml):
    print_red("Yaml file %s does not exist." % docker_compose_yml)
    return -1

  def cleanup(*args):
    shout("docker-compose -f %s -p ci stop" % docker_compose_yml, print_output=True)
  for sig in EXIT_SIGNALS:
    signal.signal(sig, cleanup)

  shout("docker-compose -f %s -p ci up --build --abort-on-container-exit" % docker_compose_yml, print_output=True)

  try:
    test_exit_code = int(shout("docker wait ci_%s_1" % config.project_name))
  except CalledProcessError:
    print_red('Docker wait failed.')
    shout("docker-compose -f %s -p ci stop" % docker_compose_yml, print_output=True)
    return -1

  if test_exit_code != 0:
    print_red('Tests Failed - Exit Code: %s\n' % test_exit_code)
  else:
    print_green("Tests Passed")

  shout("docker-compose -f %s -p ci stop" % docker_compose_yml, print_output=True)

  return test_exit_code
