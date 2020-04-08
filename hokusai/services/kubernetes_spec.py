import yaml

from tempfile import NamedTemporaryFile

from hokusai.lib.config import config
from hokusai.lib.config_loader import ConfigLoader
from hokusai.lib.template_renderer import TemplateRenderer

from hokusai.lib.exceptions import HokusaiError

class KubernetesSpec(object):
  def __init__(self, kubernetes_yaml):
    self.kubernetes_yaml = kubernetes_yaml

  def to_string(self):
    template_vars = {}

    if config.template_config_file:
      config_loader = ConfigLoader(config.template_config_file)
      _config = config_loader.load()
      if 'vars' not in _config:
        raise HokusaiError("Config does not contain key 'vars'")
      template_vars = _config['vars']

    return TemplateRenderer(self.kubernetes_yaml, template_vars).render()

  def to_file(self):
    f = NamedTemporaryFile(delete=False)
    f.write(self.to_string())
    f.close()
    return f.name

  def to_list(self):
    return list(yaml.safe_load_all(self.to_string()))
