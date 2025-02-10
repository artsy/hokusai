import os

from hokusai.lib.common import shout
from hokusai.lib.config import BUILD_YAML_FILE, config
from hokusai.lib.docker_compose_helpers import generate_compose_command


class Docker:
  def build(self, filename=None):
    env_vars = "DOCKER_DEFAULT_PLATFORM=linux/amd64"
    compose_command = generate_compose_command(
      filename,
      default_yaml_file=BUILD_YAML_FILE
    )
    opts = "--progress plain"
    build_command = f'{env_vars} {compose_command} -p hokusai build {opts}'
    if config.pre_build:
      build_command = "%s && %s" % (config.pre_build, build_command)
    if config.post_build:
      build_command = "%s && %s" % (build_command, config.post_build)
    shout(build_command, print_output=True)
