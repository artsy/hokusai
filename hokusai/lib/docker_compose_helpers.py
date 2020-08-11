import os

import yaml

from hokusai import CWD
from hokusai.lib.config import HOKUSAI_CONFIG_DIR
from hokusai.lib.exceptions import HokusaiError
from hokusai.lib.template_selector import TemplateSelector
from hokusai.services.yaml_spec import YamlSpec

def follow_extends(docker_compose_yml):
  with open(docker_compose_yml, 'r') as f:
    rendered_templates = []
    struct = yaml.safe_load(f.read())
    for service_name, service_spec in struct['services'].items():
      if 'extends' not in service_spec or 'file' not in service_spec['extends']:
        continue
      extended_filename = service_spec['extends']['file']
      extended_template_path = os.path.join(CWD, HOKUSAI_CONFIG_DIR, extended_filename)
      if not os.path.isfile(extended_template_path):
        extended_template_path = os.path.join(CWD, HOKUSAI_CONFIG_DIR, extended_filename + '.j2')
      extended_template = TemplateSelector().get(extended_template_path)
      rendered_templates.append(YamlSpec(extended_template).to_file())
    return rendered_templates
