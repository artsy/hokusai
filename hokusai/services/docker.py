import os

from hokusai import CWD
from hokusai.lib.config import HOKUSAI_CONFIG_DIR, BUILD_YAML_FILE, LEGACY_BUILD_YAML_FILE, config
from hokusai.lib.common import shout
from hokusai.lib.exceptions import HokusaiError

class Docker(object):
  def build(self, filename):
    if filename is None:
      docker_compose_yml = os.path.join(CWD, HOKUSAI_CONFIG_DIR, BUILD_YAML_FILE)
      legacy_docker_compose_yml = os.path.join(CWD, HOKUSAI_CONFIG_DIR, LEGACY_BUILD_YAML_FILE)

      if not os.path.isfile(docker_compose_yml) and not os.path.isfile(legacy_docker_compose_yml):
        raise HokusaiError("Yaml files %s / %s do not exist." % (docker_compose_yml, legacy_docker_compose_yml))

      if os.path.isfile(docker_compose_yml):
        build_command = "docker-compose -f %s -p hokusai build" % docker_compose_yml
      if os.path.isfile(legacy_docker_compose_yml):
        build_command = "docker-compose -f %s -p hokusai build" % legacy_docker_compose_yml
    else:
      build_command = "docker-compose -f %s -p hokusai build" % filename

    if config.pre_build:
      build_command = "%s && %s" % (config.pre_build, build_command)

    if config.post_build:
      build_command = "%s && %s" % (build_command, config.post_build)

    shout(build_command, print_output=True)
