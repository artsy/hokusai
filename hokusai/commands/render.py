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

  # fetch base
  fetch_base(context, tempdir)

  return tempdir

def fetch_base(context, dir):
  """obtain base specs from artsy-hokusai-templates repo and store in dir/bases"""
  git_repo = 'git@github.com:artsy/artsy-hokusai-templates.git'
  git_branch = 'artsyjian/kustomize'
  tempdir = TemporaryDirectory().name
  print("cloning remote base into dir: %s" %tempdir)
  shout("git clone -b %s --single-branch %s %s" % (git_branch, git_repo, tempdir))
  cloned_base = os.path.join(tempdir, 'kustomize/base_per_resource')
  copytree(cloned_base, dir + '/base')

  yamls = TemplateSelector().get_all(dir + '/base')
  for yaml in yamls:
    YamlSpec(yaml).to_file_in_place()

def kustomize(context):
  # jinja render the files first
  tempdir = render(context)
  print("running kustomize on dir: %s" %tempdir)
  shout("kustomize build %s" %tempdir, print_output=True)
