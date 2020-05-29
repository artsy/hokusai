import os

import yaml

from hokusai.lib.config import HOKUSAI_CONFIG_DIR
from hokusai.lib.exceptions import HokusaiError
from hokusai.lib.template_selector import TemplateSelector
from hokusai.services.yaml_spec import YamlSpec

def follow_extends(docker_compose_yml):
  with open(docker_compose_yml, 'r') as f:
    try:
      struct = yaml.safe_load(f.read())
      for service_name, service_spec in struct['services'].iteritems():
        extended_filename = service_spec['extends']['file']
        YamlSpec(TemplateSelector().get(os.path.join(HOKUSAI_CONFIG_DIR, extended_filename))).to_file()
    except Exception, err:
      if isinstance(err, HokusaiError):
        raise
      else:
        pass
