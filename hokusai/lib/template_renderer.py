from jinja2 import Template
from hokusai.lib.config_loader import ConfigLoader
from hokusai.lib.exceptions import HokusaiError

class TemplateRenderer(object):
  def __init__(self, template_path, var_path):
    self.template_path = template_path
    self.var_path = var_path

  def load_variables(self):
    configloader = ConfigLoader(self.var_path)
    config = configloader.load()
    if type(config) is not dict or "vars" not in config:
      raise HokusaiError("YAML is not valid shape")
    return config["vars"]

  def load_template(self):
    try:
      with open(self.template_path) as file_:
        template = Template(file_.read())
        return template
    except IOError: 
      raise HokusaiError("Template not found.")

  def insert_variables(self):
    vars = self.load_variables()
    template = self.load_template()
    return template.render(**vars)
