import click

import hokusai

from hokusai.cli.base import base
from hokusai.lib.common import set_verbosity, select_context, CONTEXT_SETTINGS

@base.group()
def local(context_settings=CONTEXT_SETTINGS):
  """Interact with your local project and Docker engine"""
  pass


@local.command(context_settings=CONTEXT_SETTINGS)
def build():
  """Build the Docker image defined in ./hokusai/common.yml"""
  hokusai.build()


@local.command(context_settings=CONTEXT_SETTINGS)
@click.option('-b', '--build', type=click.BOOL, is_flag=True, help='Force rebuild the docker image before running the test suite')
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, help='Verbose output')
def test(build, verbose):
  """Boot the test environment defined in ./hokusai/test.yml and run the test suite

  Return the exit code of the container with the name 'project-name' in hokusai/config.yml"""
  set_verbosity(verbose)
  hokusai.test(build)
