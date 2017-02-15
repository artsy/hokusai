from subprocess import check_call, CalledProcessError

from hokusai.config import HokusaiConfig

def images():
  config = HokusaiConfig().check()
  try:
    check_call("docker images %s" % config.aws_ecr_registry, shell=True)
  except CalledProcessError:
    return -1
  return 0
