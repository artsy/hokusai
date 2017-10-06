import click

import hokusai
from hokusai.cli.remote import remote
from hokusai.lib.common import set_verbosity, select_context, CONTEXT_SETTINGS

@remote.group()
def stack(context_settings=CONTEXT_SETTINGS):
  """Interact with the Kubernetes deployment(s) for the application"""
  pass


@stack.command(context_settings=CONTEXT_SETTINGS)
@click.option('--staging', type=click.BOOL, is_flag=True, help='Target staging')
@click.option('--production', type=click.BOOL, is_flag=True, help='Target production')
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, help='Verbose output')
def create(staging, production, verbose):
  """Create the Kubernetes stack defined in ./hokusai/{staging/production}.yml"""
  set_verbosity(verbose)
  context = select_context(staging, production)
  hokusai.stack_create(context)


@stack.command(context_settings=CONTEXT_SETTINGS)
@click.option('--staging', type=click.BOOL, is_flag=True, help='Target staging')
@click.option('--production', type=click.BOOL, is_flag=True, help='Target production')
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, help='Verbose output')
def delete(staging, production, verbose):
  """Delete the Kubernetes stack defined in ./hokusai/{staging/production}.yml"""
  set_verbosity(verbose)
  context = select_context(staging, production)
  hokusai.stack_delete(context)


@stack.command(context_settings=CONTEXT_SETTINGS)
@click.option('--staging', type=click.BOOL, is_flag=True, help='Target staging')
@click.option('--production', type=click.BOOL, is_flag=True, help='Target production')
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, help='Verbose output')
def update(staging, production, verbose):
  """Update the Kubernetes stack defined in ./hokusai/{staging/production}.yml"""
  set_verbosity(verbose)
  context = select_context(staging, production)
  hokusai.stack_update(context)


@stack.command(context_settings=CONTEXT_SETTINGS)
@click.option('--staging', type=click.BOOL, is_flag=True, help='Target staging')
@click.option('--production', type=click.BOOL, is_flag=True, help='Target production')
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, help='Verbose output')
def status(staging, production, verbose):
  """Print the Kubernetes stack status defined in ./hokusai/{staging/production}.yml"""
  set_verbosity(verbose)
  context = select_context(staging, production)
  hokusai.stack_status(context)
