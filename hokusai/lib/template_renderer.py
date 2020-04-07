from jinja2 import Template
from hokusai.lib.exceptions import HokusaiError

class TemplateRenderer(object):
  def __init__(self, template_path, template_vars):
    self.template_path = template_path
    self.template_vars = template_vars

  def load_variables(self):
    if type(self.template_vars) is not dict:
      raise HokusaiError("Provided variables are not key-value pairs")
    return self.template_vars

  def load_template(self):
    try:
      with open(self.template_path) as file_:
        template = Template(file_.read())
        return template
    except IOError: 
      raise HokusaiError("Template not found.")

  def render(self):
    _vars = self.load_variables()
    template = self.load_template()
    return template.render(**_vars)

