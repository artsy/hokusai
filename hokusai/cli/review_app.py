import click

import hokusai

from hokusai.cli.base import base
from hokusai.cli.staging import KUBE_CONTEXT
from hokusai.lib.common import set_verbosity, CONTEXT_SETTINGS, clean_string
from hokusai.lib.config import config
from hokusai.lib.namespace import create_new_app_yaml

@base.group()
def review_app(context_settings=CONTEXT_SETTINGS):
  """Create/Manage review apps"""
  pass

@review_app.command(context_settings=CONTEXT_SETTINGS)
@click.argument('app_name', type=click.STRING)
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, help='Verbose output')
@click.option('-sf', '--source-file', type=click.STRING, default='hokusai/staging.yml', help="The source yaml file from which to create the new resource file (default: hokusai/staging.yml)")
@click.option('-dn', '--destination-namespace', type=click.STRING, default=None, help="The namespace in which to create new resources")
def setup(app_name, verbose, source_file, destination_namespace):
  """Setup a new review-app - create a Yaml file based on APP_NAME --source-file and --destination-namespace"""
  set_verbosity(verbose)
  if destination_namespace is None: destination_namespace = app_name
  create_new_app_yaml(source_file, app_name, clean_string(destination_namespace))


@review_app.command(context_settings=CONTEXT_SETTINGS)
@click.argument('app_name', type=click.STRING)
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, help='Verbose output')
def create(app_name, verbose):
  """Creates the Kubernetes based resources defined in ./hokusai/{APP_NAME}.yml"""
  hokusai.k8s_create(KUBE_CONTEXT, app_name, app_name)


@review_app.command(context_settings=CONTEXT_SETTINGS)
@click.argument('app_name', type=click.STRING)
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, help='Verbose output')
@click.option('-dn', '--destination-namespace', type=click.STRING, default=None, help="The namespsace in which to create the new resource")
def env_copy(app_name, verbose, destination_namespace):
  """Copies the app's environment config map to --destination-namespace"""
  if destination_namespace is None: destination_namespace = app_name
  hokusai.k8s_copy_config(KUBE_CONTEXT, clean_string(destination_namespace))


@review_app.command(context_settings=CONTEXT_SETTINGS)
@click.argument('app_name', type=click.STRING)
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, help='Verbose output')
def update(app_name, verbose):
  """Updates the Kubernetes based resources defined in ./hokusai/{APP_NAME}.yml"""
  set_verbosity(verbose)
  hokusai.k8s_update(KUBE_CONTEXT, app_name)


@review_app.command(context_settings=CONTEXT_SETTINGS)
@click.argument('app_name', type=click.STRING)
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, help='Verbose output')
def delete(app_name, verbose):
  """Deletes the Kubernetes based resources defined in ./hokusai/{APP_NAME}.yml"""
  set_verbosity(verbose)
  hokusai.k8s_delete(KUBE_CONTEXT, app_name)
