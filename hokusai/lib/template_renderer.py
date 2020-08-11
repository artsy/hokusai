import os

from jinja2 import Environment, FileSystemLoader, StrictUndefined
from jinja2.exceptions import TemplateError

from hokusai.lib.exceptions import HokusaiError

class TemplateRenderer(object):
  def __init__(self, template_path, template_config):
    self.template_path = template_path
    self.template_config = template_config

  def load_template(self):
    try:
      env = Environment(loader=FileSystemLoader(os.path.split(self.template_path)[0]), undefined=StrictUndefined)
      return env.get_template(os.path.split(self.template_path)[1])
    except IOError:
      raise HokusaiError("Template %s not found." % self.template_path)

  def render(self):
    try:
      return self.load_template().render(**self.template_config)
    except TemplateError as e:
      raise HokusaiError("Rendering template raised error %s <message '%s'>" % (e.__class__, e.message))
