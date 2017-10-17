import click

import hokusai

from hokusai.cli.base import base
from hokusai.lib.common import set_verbosity, select_context, CONTEXT_SETTINGS

@base.group()
def remote(context_settings=CONTEXT_SETTINGS):
  """Interact with remote Kubernetes resources"""
  pass


@remote.command(context_settings=CONTEXT_SETTINGS)
@click.option('--staging', type=click.BOOL, is_flag=True, help='Target staging')
@click.option('--production', type=click.BOOL, is_flag=True, help='Target production')
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, help='Verbose output')
def create(staging, production, verbose):
  """Create the Kubernetes remote resources defined in ./hokusai/{staging/production}.yml"""
  set_verbosity(verbose)
  context = select_context(staging, production)
  hokusai.environment_create(context)


@remote.command(context_settings=CONTEXT_SETTINGS)
@click.option('--staging', type=click.BOOL, is_flag=True, help='Target staging')
@click.option('--production', type=click.BOOL, is_flag=True, help='Target production')
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, help='Verbose output')
def delete(staging, production, verbose):
  """Delete the Kubernetes remote resources defined in ./hokusai/{staging/production}.yml"""
  set_verbosity(verbose)
  context = select_context(staging, production)
  hokusai.environment_delete(context)


@remote.command(context_settings=CONTEXT_SETTINGS)
@click.option('--staging', type=click.BOOL, is_flag=True, help='Target staging')
@click.option('--production', type=click.BOOL, is_flag=True, help='Target production')
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, help='Verbose output')
def update(staging, production, verbose):
  """Update the Kubernetes remote resources defined in ./hokusai/{staging/production}.yml"""
  set_verbosity(verbose)
  context = select_context(staging, production)
  hokusai.environment_update(context)


@remote.command(context_settings=CONTEXT_SETTINGS)
@click.option('--staging', type=click.BOOL, is_flag=True, help='Target staging')
@click.option('--production', type=click.BOOL, is_flag=True, help='Target production')
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, help='Verbose output')
def status(staging, production, verbose):
  """Print the Kubernetes remote resources status defined in ./hokusai/{staging/production}.yml"""
  set_verbosity(verbose)
  context = select_context(staging, production)
  hokusai.environment_status(context)


@remote.command(context_settings=CONTEXT_SETTINGS)
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, help='Verbose output')
def gitdiff(verbose):
  """Print a git diff between the tag currently deployed on production
  and the tag currently deployed on staging"""
  set_verbosity(verbose)
  hokusai.gitdiff()


@remote.command(context_settings=CONTEXT_SETTINGS)
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, help='Verbose output')
def gitlog(verbose):
  """Print a git log between the tag currently deployed on production
  and the tag currently deployed on staging"""
  set_verbosity(verbose)
  hokusai.gitlog()


@remote.command(context_settings=CONTEXT_SETTINGS)
@click.argument('command', type=click.STRING)
@click.option('--staging', type=click.BOOL, is_flag=True, help='Target staging')
@click.option('--production', type=click.BOOL, is_flag=True, help='Target production')
@click.option('--tty', type=click.BOOL, is_flag=True, help='Attach the terminal')
@click.option('--tag', type=click.STRING, help='The image tag to run (defaults to either staging or production)')
@click.option('--env', type=click.STRING, multiple=True, help='Environment variables in the form of "KEY=VALUE"')
@click.option('--constraint', type=click.STRING, multiple=True, help='Constrain command to run on nodes matching labels in the form of "key=value"')
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, help='Verbose output')
def run(command, staging, production, tty, tag, env, constraint, verbose):
  """Launch a new container and run a command in a given environment"""
  set_verbosity(verbose)
  context = select_context(staging, production)
  hokusai.run(context, command, tty, tag, env, constraint)


@remote.command(context_settings=CONTEXT_SETTINGS)
@click.option('--staging', type=click.BOOL, is_flag=True, help='Target staging')
@click.option('--production', type=click.BOOL, is_flag=True, help='Target production')
@click.option('-t', '--timestamps', type=click.BOOL, is_flag=True, help='Include timestamps')
@click.option('-f', '--follow', type=click.BOOL, is_flag=True, help='Follow logs')
@click.option('-t', '--tail', type=click.INT, help="Number of lines of recent logs to display")
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, help='Verbose output')
def logs(staging, production, timestamps, follow, tail, verbose):
  """Get container logs for a given environment"""
  set_verbosity(verbose)
  context = select_context(staging, production)
  hokusai.logs(context, timestamps, follow, tail)
