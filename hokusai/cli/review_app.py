import click

import hokusai

from hokusai.cli.base import base
from hokusai.cli.staging import KUBE_CONTEXT
from hokusai.lib.common import set_verbosity, CONTEXT_SETTINGS, clean_string
from hokusai.lib.config import config
from hokusai.lib.namespace import create_new_app_yaml

@base.group()
def review_app(context_settings=CONTEXT_SETTINGS):
  """Manage/Create review apps"""
  pass

@review_app.command(context_settings=CONTEXT_SETTINGS)
@click.argument('app_name', type=click.STRING)
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, help='Verbose output')
@click.option('-sf', '--source-file', type=click.STRING, default='hokusai/staging.yml')
@click.option('-dn', '--destination-namespace', type=click.STRING, default=None)
def setup(app_name, verbose, source_file, destination_namespace):
  set_verbosity(verbose)
  # create app_name.yaml file based on source_file
  if destination_namespace is None: destination_namespace = app_name
  destination_namespace = clean_string(destination_namespace)
  create_new_app_yaml(source_file, app_name, destination_namespace)


@review_app.command(context_settings=CONTEXT_SETTINGS)
@click.argument('app_name', type=click.STRING)
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, help='Verbose output')
@click.option('-dn', '--destination-namespace', type=click.STRING, default=None)
def create(app_name, verbose, destination_namespace):
  if destination_namespace is None: destination_namespace = app_name
  destination_namespace = clean_string(destination_namespace)
  hokusai.k8s_create(KUBE_CONTEXT, app_name, app_name)

@review_app.command(context_settings=CONTEXT_SETTINGS)
@click.argument('app_name', type=click.STRING)
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, help='Verbose output')
@click.option('-dn', '--destination-namespace', type=click.STRING, default=None)
def env_copy(app_name, verbose, destination_namespace):
  if destination_namespace is None: destination_namespace = app_name
  destination_namespace = clean_string(destination_namespace)
  hokusai.k8s_copy_config(KUBE_CONTEXT, destination_namespace)

@review_app.command(context_settings=CONTEXT_SETTINGS)
@click.argument('app_name', type=click.STRING)
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, help='Verbose output')
def update(app_name, verbose):
  """Updates the Kubernetes based resources defined in ./hokusai/%s.yml""" % app_name
  set_verbosity(verbose)
  hokusai.k8s_update(KUBE_CONTEXT, app_name)