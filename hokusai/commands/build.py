from subprocess import check_call, CalledProcessError


from hokusai.config import HokusaiConfig
from hokusai.common import *

def build():
  config = HokusaiConfig().check()
  docker_compose_yml = os.path.join(os.getcwd(), 'hokusai/common.yml')
  try:
    check_call("docker-compose -f %s -p build build" % docker_compose_yml, shell=True)
    print_green("Built build_%s:latest" % config.project_name)
  except CalledProcessError:
    print_red('Build failed')
    return -1
  return 0
