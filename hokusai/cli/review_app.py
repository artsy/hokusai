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
  create_new_app_yaml('hokusai/staging.yml', app_name)

def create_new_app_yaml(original_yaml_file, app_name, current_namespace='default'):
  with open(original_yaml_file, 'r') as stream:
    try:
      yaml_content = list(yaml.load_all(stream))
      # @TODO: replace namespace: default with new namespace name
      # prepend new namespace definition to yaml
      new_namespace = {"apiVersion": "v1", "kind": "Namespace", "meta": { "name": str(app_name) }}
      yaml_content = [new_namespace] + yaml_content
      with open("hokusai/%s.yml" % app_name, 'w') as output:
        yaml.dump_all(yaml_content, output)
    except yaml.YAMLError as exc:
      print(exc)
