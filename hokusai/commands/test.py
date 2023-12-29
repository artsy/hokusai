import os
import signal

from hokusai import CWD
from hokusai.lib.config import HOKUSAI_CONFIG_DIR, TEST_YML_FILE, config
from hokusai.lib.common import print_green, print_red, shout, EXIT_SIGNALS
from hokusai.lib.exceptions import CalledProcessError, HokusaiError
from hokusai.services.docker import Docker
from hokusai.lib.template_selector import TemplateSelector
from hokusai.lib.docker_compose_helpers import follow_extends
from hokusai.services.yaml_spec import YamlSpec

def test(build, cleanup, filename, service_name):
  if filename is None:
    yaml_template = TemplateSelector().get(os.path.join(CWD, HOKUSAI_CONFIG_DIR, TEST_YML_FILE))
  else:
    yaml_template = TemplateSelector().get(filename)

  docker_compose_yml = YamlSpec(yaml_template).to_file()
  follow_extends(docker_compose_yml)

  def on_cleanup(*args):
    shout("COMPOSE_COMPATIBILITY=true docker-compose -f %s -p hokusai stop" % docker_compose_yml)
    shout("COMPOSE_COMPATIBILITY=true docker-compose -f %s -p hokusai rm --force" % docker_compose_yml)

  if cleanup:
    for sig in EXIT_SIGNALS:
      signal.signal(sig, on_cleanup)

  if build:
    Docker().build(filename=yaml_template)

  if service_name is None:
    service_name = config.project_name

  opts = " --abort-on-container-exit --exit-code-from %s" % service_name

  print_green("Starting test environment... Press Ctrl+C to stop.", newline_after=True)
  try:
    return_code = int(shout("COMPOSE_COMPATIBILITY=true docker-compose -f %s -p hokusai up%s" % (docker_compose_yml, opts), print_output=True))
  except CalledProcessError as e:
    print_red("CalledProcessError return code: %s" % e.returncode)
    if cleanup: on_cleanup()
    raise HokusaiError('Tests Failed')

  if return_code:
    raise HokusaiError('Tests Failed - Exit Code: %s\n' % return_code, return_code=return_code)
  else:
    print_green("Tests Passed")

  if cleanup: on_cleanup()

  return return_code
