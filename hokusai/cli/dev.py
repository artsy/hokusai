import click

import hokusai

from hokusai.cli.local import local
from hokusai.lib.common import set_verbosity, CONTEXT_SETTINGS

@local.group()
def dev(context_settings=CONTEXT_SETTINGS):
  """Interact with the local docker-compose development stack defined in ./hokusai/development.yml"""
  pass

@dev.command(context_settings=CONTEXT_SETTINGS)
@click.option('-b', '--build', type=click.BOOL, is_flag=True, help="Force rebuild the docker image before running")
@click.option('-d', '--detach', type=click.BOOL, is_flag=True, help="Run containers in the background")
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, help='Verbose output')
def start(build, detach, verbose):
  """Start the development stack defined in ./hokusai/development.yml"""
  set_verbosity(verbose)
  hokusai.dev_start(build, detach)


@dev.command(context_settings=CONTEXT_SETTINGS)
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, help='Verbose output')
def stop(verbose):
  """Stop the development stack defined in ./hokusai/development.yml"""
  set_verbosity(verbose)
  hokusai.dev_stop()


@dev.command(context_settings=CONTEXT_SETTINGS)
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, help='Verbose output')
def status(verbose):
  """Print the status of the development stack"""
  set_verbosity(verbose)
  hokusai.dev_status()


@dev.command(context_settings=CONTEXT_SETTINGS)
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, help='Verbose output')
@click.option('-f', '--follow', type=click.BOOL, is_flag=True, help="Follow output")
@click.option('-t', '--tail', type=click.BOOL, is_flag=True, help="Same as '--follow'")
def logs(follow, tail, verbose):
  """Print logs from the development stack"""
  set_verbosity(verbose)
  hokusai.dev_logs(follow or tail)


@dev.command(context_settings=CONTEXT_SETTINGS)
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, help='Verbose output')
def shell(verbose):
  """Attach a shell session to the stack's project container"""
  set_verbosity(verbose)
  hokusai.dev_shell()


@dev.command(context_settings=CONTEXT_SETTINGS)
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, help='Verbose output')
def clean(verbose):
  """Stop and remove all containers in the stack"""
  set_verbosity(verbose)
  hokusai.dev_clean()
