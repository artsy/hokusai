from collections import OrderedDict
import click
<<<<<<< HEAD
=======

>>>>>>> 026377db6f5958ef9b6b7f30b7e89ad256609ceb
from shutil import copyfile
import yaml

import hokusai

from hokusai.cli.base import base
from hokusai.cli.staging import KUBE_CONTEXT
from hokusai.lib.common import set_verbosity, CONTEXT_SETTINGS
from hokusai.lib.config import config

@base.group()
def review_app(context_settings=CONTEXT_SETTINGS):
  """Manage/Create review apps"""
  pass

@review_app.command(context_settings=CONTEXT_SETTINGS)
@click.argument('app_name', type=click.STRING)
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, help='Verbose output')
@click.option('-sf', '--source-file', type=click.STRING, default='hokusai/staging.yml', help='Source deployment file')
@click.option('-dn', '--destination-namespace', type=click.STRING, default=None, help='Target Namespace')
def create(app_name, verbose, source_file, source_namespace, destination_namespace):
  set_verbosity(verbose)
  # copy staging yml file
  if destination_namespace is None: destination_namespace = app_name
  create_new_app_yaml(source_file, app_name, destination_namespace)

def create_new_app_yaml(source_file, app_name, destination_namespace):
  with open(source_file, 'r') as stream:
    try:
      yaml_content = list(yaml.load_all(stream))
      # update namespace to destination namespace
      for c in yaml_content: update_namespace(c, destination_namespace)
      # prepend new namespace definition to yaml
      new_namespace = OrderedDict([
          ('apiVersion', 'v1'),
          ('kind', 'Namespace'),
          ('metadata', {
            'name': str(app_name)
          })
        ])
      yaml_content = [new_namespace] + yaml_content
      with open("hokusai/%s.yml" % app_name, 'w') as output:
        yaml.safe_dump_all(yaml_content, output, default_flow_style=False)
    except yaml.YAMLError as exc:
      print(exc)

def update_namespace(yaml_section, destination_namespace):
  if 'namespace' in yaml_section: yaml_section['namespace'] = destination_namespace
  for k, v in yaml_section.iteritems():
    if isinstance(v, dict):
      update_namespace(v, destination_namespace)
