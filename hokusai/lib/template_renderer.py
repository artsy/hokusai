import os

from jinja2 import Environment, FileSystemLoader, StrictUndefined
from jinja2.exceptions import TemplateError

from hokusai.lib.exceptions import HokusaiError

class TemplateRenderer:
  def __init__(self, template_path, template_config):
    self.template_path = template_path
    self.template_config = template_config

  def load_template(self, render_template=True):
    try:
      if render_template:
        env = Environment(loader=FileSystemLoader(os.path.split(self.template_path)[0]), undefined=StrictUndefined)
      else:
        env = Environment(loader=FileSystemLoader(os.path.split(self.template_path)[0]), undefined=StrictUndefined, trim_blocks=True,block_start_string='@@',block_end_string='@@',variable_start_string='@=', variable_end_string='=@')
      return env.get_template(os.path.split(self.template_path)[1])
    except IOError:
      raise HokusaiError("Template %s not found." % self.template_path)

  def render(self, render_template=True):
    return self.load_template(render_template).render(**self.template_config)
