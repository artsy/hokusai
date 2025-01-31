import os

from hokusai import CWD
from hokusai.lib.config import HOKUSAI_CONFIG_DIR, BUILD_YAML_FILE, config
from hokusai.lib.common import shout, get_verbosity, print_yellow, print_green
from hokusai.lib.template_selector import TemplateSelector
from hokusai.services.yaml_spec import YamlSpec
from hokusai.lib.exceptions import CalledProcessError
from hokusai.lib.docker_compose_helpers import generate_compose_command


class Docker:
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

  def build(self, filename=None):
    env_vars = "DOCKER_DEFAULT_PLATFORM=linux/amd64"
    compose_command = generate_compose_command(filename, default_yaml_file=BUILD_YAML_FILE)
    opts = "--progress plain"
    build_command = f'{env_vars} {compose_command} -p hokusai build {opts}'
    if config.pre_build:
      build_command = "%s && %s" % (config.pre_build, build_command)
    if config.post_build:
      build_command = "%s && %s" % (build_command, config.post_build)
    shout(build_command, print_output=True)
