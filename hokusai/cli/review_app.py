from collections import OrderedDict
import click
import yaml

import hokusai

from hokusai.cli.base import base
from hokusai.cli.staging import KUBE_CONTEXT
from hokusai.lib.common import set_verbosity, CONTEXT_SETTINGS, clean_string
from hokusai.lib.config import config
from hokusai.lib.exceptions import HokusaiError

@base.group()
def review_app(context_settings=CONTEXT_SETTINGS):
  """Manage/Create review apps"""
  pass

@review_app.command(context_settings=CONTEXT_SETTINGS)
@click.argument('app_name', type=click.STRING)
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, help='Verbose output')
@click.option('-sf', '--source-file', type=click.STRING, default='hokusai/staging.yml', help='Source deployment file')
@click.option('-dn', '--destination-namespace', type=click.STRING, default=None, help='Target Namespace')
def setup(app_name, verbose, source_file, destination_namespace):
  set_verbosity(verbose)
  # create app_name.yaml file based on source_file
  if destination_namespace is None: destination_namespace = app_name
  destination_namespace = clean_string(destination_namespace)
  create_new_app_yaml(source_file, app_name, destination_namespace)


@review_app.command(context_settings=CONTEXT_SETTINGS)
@click.argument('app_name', type=click.STRING)
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, help='Verbose output')
@click.option('-dn', '--destination-namespace', type=click.STRING, default=None, help='Target Namespace')
def create(app_name, verbose, destination_namespace):
  if destination_namespace is None: destination_namespace = app_name
  destination_namespace = clean_string(destination_namespace)
  hokusai.k8s_create(KUBE_CONTEXT, app_name, app_name)
  hokusai.k8s_copy_config(KUBE_CONTEXT, destination_namespace)

@review_app.command(context_settings=CONTEXT_SETTINGS)
@click.argument('app_name', type=click.STRING)
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, help='Verbose output')
def update(app_name, verbose):
  """Updates the Kubernetes based resources defined in ./hokusai/%s.yml""" % app_name
  set_verbosity(verbose)
  hokusai.k8s_update(KUBE_CONTEXT, app_name)

def create_new_app_yaml(source_file, app_name, destination_namespace):
  with open(source_file, 'r') as stream:
    try:
      yaml_content = list(yaml.load_all(stream))
      # update namespace to destination namespace
      for c in yaml_content: update_namespace(c, destination_namespace)
      new_namespace = OrderedDict([
          ('apiVersion', 'v1'),
          ('kind', 'Namespace'),
          ('metadata', {
            'name': destination_namespace
          })
        ])
      yaml_content = [new_namespace] + yaml_content
      with open("hokusai/%s.yml" % app_name, 'w') as output:
        yaml.safe_dump_all(yaml_content, output, default_flow_style=False)
    except yaml.YAMLError as exc:
      raise HokusaiError("Cannot read source yaml.")

def update_namespace(yaml_section, destination_namespace):
  if 'namespace' in yaml_section: yaml_section['namespace'] = destination_namespace
  for _k, v in yaml_section.iteritems():
    if isinstance(v, dict):
      update_namespace(v, destination_namespace)
