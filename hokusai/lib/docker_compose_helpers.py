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
    try:
      struct = yaml.safe_load(f.read())
      for service_name, service_spec in struct['services'].iteritems():
        extended_filename = service_spec['extends']['file']
        extended_template = TemplateSelector().get(os.path.join(CWD, HOKUSAI_CONFIG_DIR, extended_filename))
        rendered_templates.append(YamlSpec(extended_template).to_file())
    except Exception, err:
      if isinstance(err, HokusaiError):
        raise
      else:
        pass
    return rendered_templates
