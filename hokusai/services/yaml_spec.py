import os

import atexit
import jinja2
import yaml

from tempfile import NamedTemporaryFile

from botocore.exceptions import NoCredentialsError

from hokusai.lib.config import config, HOKUSAI_TMP_DIR
from hokusai.lib.config_loader import ConfigLoader
from hokusai.lib.template_renderer import TemplateRenderer
from hokusai.lib.common import print_yellow
from hokusai.lib.exceptions import HokusaiError

from hokusai.services.ecr import ECR


class YamlSpec:
  def __init__(self, template_file):
    self.template_file = template_file
    self.ecr = ECR()
    self.tmp_filename = None
    atexit.register(self.cleanup)

  def to_string(self, render_template=True):
    template_config = {
      "project_name": config.project_name
    }

    try:
      template_config["project_repo"] = self.ecr.project_repo
    except NoCredentialsError:
      print_yellow("WARNING: Could not get template variable project_repo")

    if config.template_config_files:
      for template_config_file in config.template_config_files:
        try:
          config_loader = ConfigLoader(template_config_file)
          template_config.update(config_loader.load())
        except NoCredentialsError:
          print_yellow("WARNING: Could not get template config file %s" % template_config_file)

    return TemplateRenderer(self.template_file, template_config).render(render_template)

  def to_file(self, render_template=True):
    file_basename = os.path.basename(self.template_file)
    if file_basename.endswith('.j2'):
      file_basename = file_basename.rstrip('.j2')
    f = NamedTemporaryFile(delete=False, dir=HOKUSAI_TMP_DIR, mode='w')
    self.tmp_filename = f.name
    f.write(self.to_string(render_template))
    f.close()
    return f.name

  def to_list(self, render_template=True):
    return list(yaml.safe_load_all(self.to_string(render_template)))

  def cleanup(self):
    if os.environ.get('DEBUG'):
      return
    try:
      os.unlink(self.tmp_filename)
    except:
      pass
