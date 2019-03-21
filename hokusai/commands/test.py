import os
import signal

from hokusai import CWD
from hokusai.lib.command import command
from hokusai.lib.config import HOKUSAI_CONFIG_DIR, TEST_YML_FILE, config
from hokusai.lib.common import print_green, shout, EXIT_SIGNALS
from hokusai.lib.exceptions import CalledProcessError, HokusaiError
from hokusai.services.docker import Docker

@command()
def test(build, cleanup):
  docker_compose_yml = os.path.join(CWD, HOKUSAI_CONFIG_DIR, TEST_YML_FILE)
  if not os.path.isfile(docker_compose_yml):
    raise HokusaiError("Yaml file %s does not exist." % docker_compose_yml)

  def on_cleanup(*args):
    shout("docker-compose -f %s -p hokusai stop" % docker_compose_yml)
    shout("docker-compose -f %s -p hokusai rm --force" % docker_compose_yml)

  if cleanup:
    for sig in EXIT_SIGNALS:
      signal.signal(sig, on_cleanup)

  opts = ' --abort-on-container-exit'
  if build:
    Docker().build()

  print_green("Starting test environment... Press Ctrl+C to stop.")
  try:
    shout("docker-compose -f %s -p hokusai up%s" % (docker_compose_yml, opts), print_output=True)
    return_code = int(shout("docker wait hokusai_%s_1" % config.project_name))
  except CalledProcessError:
    if cleanup: on_cleanup()
    raise HokusaiError('Tests Failed')

  if return_code:
    raise HokusaiError('Tests Failed - Exit Code: %s\n' % return_code, return_code=return_code)
  else:
    print_green("Tests Passed")

  if cleanup: on_cleanup()

  return return_code
