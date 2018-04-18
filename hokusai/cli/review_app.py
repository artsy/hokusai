import click
from shutil import copyfile
import yaml

import hokusai

from hokusai.cli.staging import staging, KUBE_CONTEXT
from hokusai.lib.common import set_verbosity, CONTEXT_SETTINGS
from hokusai.lib.config import config

@staging.group()
def review_app(context_settings=CONTEXT_SETTINGS):
  """Manage/Create review apps"""
  pass

@review_app.command(context_settings=CONTEXT_SETTINGS)
@click.argument('app_name', type=click.STRING)
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, help='Verbose output')
def create(app_name, verbose):
  set_verbosity(verbose)
  # copy staging yml file
  pr_file_name = "hokusai/%s.yml" % app_name
  copyfile('hokusai/staging.yml', pr_file_name)

def change_namespace(original_yaml_file, new_namespace, current_namespace='default'):
  with open(original_yaml_file, 'r') as stream:
    try:
      yaml_content = yaml.load(stream)
    except yaml.YAMLError as exc:
      print(exc)
