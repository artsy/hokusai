import os

from hokusai import CWD
from hokusai.lib.config import HOKUSAI_CONFIG_DIR, BUILD_YAML_FILE, config
from hokusai.lib.common import shout, get_verbosity, print_yellow, print_green
from hokusai.lib.template_selector import TemplateSelector
from hokusai.services.yaml_spec import YamlSpec

from hokusai.lib.exceptions import CalledProcessError

class Docker:
  def build(self, filename=None):
    if filename is None:
      yaml_template = TemplateSelector().get(os.path.join(CWD, HOKUSAI_CONFIG_DIR, BUILD_YAML_FILE))
    else:
      yaml_template = TemplateSelector().get(filename)

    docker_compose_yml = YamlSpec(yaml_template).to_file()

    # docker-compose v2 switched to using '-' as separator in image name, resulting in 'hokusai-<project>'
    # COMPOSE_COMPATIBILITY=true forces v2 to use '_', resulting in 'hokusai_<project>', matching v1
    env_vars = "DOCKER_DEFAULT_PLATFORM=linux/amd64 COMPOSE_COMPATIBILITY=true"

    compose_command = f"docker compose -f {docker_compose_yml} -p hokusai build"
    compose_options = "--progress plain"
    build_command = f"{env_vars} {compose_command} {compose_options}"

    if config.pre_build:
      build_command = "%s && %s" % (config.pre_build, build_command)

    if config.post_build:
      build_command = "%s && %s" % (build_command, config.post_build)

    shout(build_command, print_output=True)

  @classmethod
  def compose_command(cls):
    ''' decide what command to use for Docker Compose '''
    command_to_use = ''
    try:
      shout('which docker-compose')
      if get_verbosity():
        print_green('Found docker-compose.')
      command_to_use = 'docker-compose'
    except CalledProcessError:
      if get_verbosity():
        print_yellow(
          'docker-compose command not found. Will use "docker compose".'
        )
      command_to_use = 'docker compose'
    return command_to_use
