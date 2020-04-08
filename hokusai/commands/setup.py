import os
import sys
import time
import urllib
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
from hokusai.lib.exceptions import HokusaiError

@command(config_check=False)
def setup(project_name, template_remote, template_dir, template_vars, allow_missing_vars):
  mkpath(os.path.join(CWD, HOKUSAI_CONFIG_DIR))
  config.create(clean_string(project_name))

  ecr = ECR()
  if ecr.project_repo_exists():
    print_green("Project repo %s already exists.  Skipping create." % ecr.project_repo)
  else:
    ecr.create_project_repo()
    print_green("Created project repo %s" % ecr.project_repo)

  scratch_dir = None
  if template_remote:
    scratch_dir = tempfile.mkdtemp()
    git_repo_and_branch = template_remote.split('#', 1)
    git_repo = git_repo_and_branch[0]
    if len(git_repo_and_branch) == 2:
      git_branch = git_repo_and_branch[1]
    else:
      git_branch = "master"
    shout("git clone -b %s --single-branch %s %s" % (git_branch, git_repo, scratch_dir))

  custom_template_dir = None
  if allow_missing_vars:
    environment_kwargs = {}
  else:
    environment_kwargs = { "undefined": StrictUndefined }

  if scratch_dir and template_dir:
    custom_template_dir = os.path.join(scratch_dir, os.path.basename(template_dir))
    env = Environment(loader=FileSystemLoader(os.path.join(scratch_dir, os.path.basename(template_dir))), **environment_kwargs)
  elif scratch_dir:
    custom_template_dir = scratch_dir
    env = Environment(loader=FileSystemLoader(scratch_dir), **environment_kwargs)
  elif template_dir:
    custom_template_dir = os.path.abspath(template_dir)
    env = Environment(loader=FileSystemLoader(os.path.abspath(template_dir)), **environment_kwargs)
  else:
    try:
      base_path = sys._MEIPASS
      env = Environment(loader=FileSystemLoader(os.path.join(base_path, 'hokusai', 'templates')))
    except:
      env = Environment(loader=PackageLoader('hokusai', 'templates'))

  required_templates = [
    'Dockerfile.j2',
    '.dockerignore.j2',
    'hokusai/build.yml.j2',
    'hokusai/development.yml.j2',
    'hokusai/test.yml.j2',
    'hokusai/staging.yml.j2',
    'hokusai/production.yml.j2'
  ]

  template_context = {
    "project_name": config.project_name,
    "project_repo": ecr.project_repo
  }

  for s in template_vars:
    if '=' not in s:
      raise HokusaiError("Error: template variables must be of the form 'key=value'")
    split = s.split('=', 1)
    template_context[split[0]] = split[1]

  try:
    for template in required_templates:
      if custom_template_dir and not os.path.isfile(os.path.join(custom_template_dir, template)):
        raise HokusaiError("Could not find required template file %s" % template)
      with open(os.path.join(CWD, template.rstrip('.j2')), 'w') as f:
        f.write(env.get_template(template).render(**template_context))
      print_green("Created %s" % template.rstrip('.j2'))

    if custom_template_dir:
      for root, _, files in os.walk(custom_template_dir):
        subpath = os.path.relpath(root, custom_template_dir)
        if subpath is not '.':
          mkpath(os.path.join(CWD, subpath))
        for file in files:
          if subpath is not '.':
            file_path = os.path.join(subpath, file)
          else:
            file_path = file
          if file_path in required_templates:
            continue
          if file_path.endswith('.j2'):
            with open(os.path.join(CWD, file_path.rstrip('.j2')), 'w') as f:
              f.write(env.get_template(file_path).render(**template_context))
          else:
            copyfile(os.path.join(custom_template_dir, file_path), os.path.join(CWD, file_path))
          print_green("Created %s" % file_path.rstrip('.j2'))
  finally:
    if scratch_dir:
      rmtree(scratch_dir)
