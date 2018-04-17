import click
from shutil import copyfile, rmtree
import fileinput

import hokusai

from hokusai.cli.staging import staging, KUBE_CONTEXT
from hokusai.lib.common import set_verbosity, CONTEXT_SETTINGS
from hokusai.lib.config import config

@staging.group()
def review_app(verbose):
  """Manage/Create review apps"""
  set_verbosity(verbose)
  hokusai.k8s_status(KUBE_CONTEXT)

@review_app.comand(context_settings=CONTEXT_SETTINGS)
@click.argument('pr_number', type=click.STRING)
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, help='Verbose output')
def create(pr_number, verbose):
  set_verbosity(verbose)
  # copy staging yml file
  pr_file_name = "hokusai/%s.yml" % pr_number
  pr_project_name = "{0}_{1}".format(config.project_name, pr_number)
  copyfile('hokusai/staging.yml', pr_file_name)
  # rename app name
  for line in fileinput.input(pr_file_name, inplace=True):
    print line.replace(config.project_name, pr_project_name)
  hokusai.k8s_create(KUBE_CONTEXT, pr_number, pr_number)
  # delete pr file
  rmtree(pr_file_name)

@review_app.comand(context_settings=CONTEXT_SETTINGS)
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, help='Verbose output')
def list(verbose):
  set_verbosity(verbose)
  
