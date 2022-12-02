import os
import sys
import time
import tempfile

from shutil import rmtree, copyfile
from distutils.dir_util import mkpath

import yaml

from jinja2 import Environment, PackageLoader, FileSystemLoader, StrictUndefined

from hokusai import CWD
from hokusai.lib.command import command
from hokusai.lib.config import HOKUSAI_CONFIG_DIR, config
from hokusai.services.ecr import ECR
from hokusai.lib.common import print_green, clean_string, shout
from hokusai.lib.environment import templates_dir_path
from hokusai.lib.exceptions import HokusaiError

from hokusai.lib.template_selector import TemplateSelector

from hokusai.services.yaml_spec import YamlSpec

from tempfile import TemporaryDirectory

import shutil

def render(context):
  source_dir = os.path.join(CWD, HOKUSAI_CONFIG_DIR, context)
  # replicate context of source dir into a temp dir
  tempdir = TemporaryDirectory().name
  shutil.copytree(source_dir, tempdir)
  # list out all template files in tempdir
  yamls = TemplateSelector().get_all(tempdir)
  for yaml in yamls:
    YamlSpec(yaml).to_file_in_place()
  return tempdir

def kustomize(context):
  # jinja render the files first
  tempdir = render(context)
  shout("kustomize build %s" %tempdir, print_output=True)
