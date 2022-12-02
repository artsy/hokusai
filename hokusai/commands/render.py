import os
from shutil import copytree
from tempfile import TemporaryDirectory

from hokusai import CWD
from hokusai.lib.config import HOKUSAI_CONFIG_DIR
from hokusai.lib.common import shout
from hokusai.lib.template_selector import TemplateSelector
from hokusai.services.yaml_spec import YamlSpec

def render(context):
  source_dir = os.path.join(CWD, HOKUSAI_CONFIG_DIR, context)
  # replicate context of source dir into a temp dir
  tempdir = TemporaryDirectory().name
  copytree(source_dir, tempdir)
  # list out all template files in tempdir
  yamls = TemplateSelector().get_all(tempdir)
  for yaml in yamls:
    YamlSpec(yaml).to_file_in_place()
  return tempdir

def kustomize(context):
  # jinja render the files first
  tempdir = render(context)
  shout("kustomize build %s" %tempdir, print_output=True)
