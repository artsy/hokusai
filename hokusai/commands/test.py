from subprocess import call, check_output, CalledProcessError

from hokusai.config import HokusaiConfig
from hokusai.common import *

def test():
  config = HokusaiConfig().check()
  docker_compose_yml = os.path.join(os.getcwd(), 'hokusai/test.yml')
  if not os.path.isfile(docker_compose_yml):
    print_red("Yaml file %s does not exist." % docker_compose_yml)
    return -1

  # stop any running containers
  def cleanup(*args):
    print_red('Tests Failed For Unexpected Reasons\n')
    call("docker-compose -f %s -p ci stop" % docker_compose_yml, shell=True)
    return -1

  # catch exit, do cleanup
  for sig in EXIT_SIGNALS:
    signal.signal(sig, cleanup)

  # build and run the composed services
  if call("docker-compose -f %s -p ci up --build -d" % docker_compose_yml, shell=True) != 0:
    print_red("Docker Compose Failed\n")
    return -1

  # wait for the test service to complete and grab the exit code
  try:
    test_exit_code = int(check_output("docker wait ci_%s_1" % config.project_name, shell=True))
  except CalledProcessError:
    print_red('Docker wait failed.')
    call("docker-compose -f %s -p ci stop" % docker_compose_yml, shell=True)
    return -1

  # output the logs for the test (for clarity)
  call("docker logs ci_%s_1" % config.project_name, shell=True)

  # inspect the output of the test and display respective message
  if test_exit_code != 0:
    print_red('Tests Failed - Exit Code: %s\n' % test_exit_code)
  else:
    print_green("Tests Passed")

  # cleanup
  call("docker-compose -f %s -p ci stop" % docker_compose_yml, shell=True)

  return test_exit_code
