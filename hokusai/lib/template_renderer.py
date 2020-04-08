from jinja2 import Template, StrictUndefined
from jinja2.exceptions import UndefinedError

from hokusai.lib.exceptions import HokusaiError

class TemplateRenderer(object):
  def __init__(self, template_path, template_config):
    self.template_path = template_path
    self.template_config = template_config

  def load_template(self):
    try:
      with open(self.template_path) as file_:
        template = Template(file_.read(), undefined=StrictUndefined)
        return template
    except IOError:
      raise HokusaiError("Template not found.")

  def render(self):
    template = self.load_template()
    try:
      return template.render(**self.template_config)
    except UndefinedError, e:
      raise HokusaiError("Rendering template raised error %s" % repr(e))
