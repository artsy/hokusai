import os

from hokusai import CWD
from hokusai.lib.config import HOKUSAI_CONFIG_DIR, BUILD_YAML_FILE, config
from hokusai.lib.common import shout
from hokusai.lib.template_selector import TemplateSelector
from hokusai.services.yaml_spec import YamlSpec

class Docker(object):
  def build(self, filename=None):
    if filename is None:
      yaml_template = TemplateSelector().get(os.path.join(CWD, HOKUSAI_CONFIG_DIR, BUILD_YAML_FILE))
    else:
      yaml_template = TemplateSelector().get(filename)

    docker_compose_yml = YamlSpec(yaml_template).to_file()
    build_command = "docker-compose -f %s -p hokusai build" % docker_compose_yml

    if config.pre_build:
      build_command = "%s && %s" % (config.pre_build, build_command)

    if config.post_build:
      build_command = "%s && %s" % (build_command, config.post_build)

    shout(build_command, print_output=True)
