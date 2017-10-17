import click

import hokusai
from hokusai.cli.remote import remote
from hokusai.lib.common import set_verbosity, select_context, CONTEXT_SETTINGS

@remote.group()
def env(context_settings=CONTEXT_SETTINGS):
  """Interact with the runtime environment for the application"""
  pass


@env.command(context_settings=CONTEXT_SETTINGS)
@click.option('--staging', type=click.BOOL, is_flag=True, help='Target staging')
@click.option('--production', type=click.BOOL, is_flag=True, help='Target production')
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, help='Verbose output')
def create(staging, production, verbose):
  """Create the Kubernetes configmap object `{project_name}-environment`"""
  set_verbosity(verbose)
  context = select_context(staging, production)
  hokusai.create_env(context)


@env.command(context_settings=CONTEXT_SETTINGS)
@click.argument('env_vars', type=click.STRING, nargs=-1)
@click.option('--staging', type=click.BOOL, is_flag=True, help='Target staging')
@click.option('--production', type=click.BOOL, is_flag=True, help='Target production')
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, help='Verbose output')
def get(env_vars, staging, production, verbose):
  """Print environment variables stored on the Kubernetes server"""
  set_verbosity(verbose)
  context = select_context(staging, production)
  hokusai.get_env(context, env_vars)


@env.command(context_settings=CONTEXT_SETTINGS)
@click.argument('env_vars', type=click.STRING, nargs=-1)
@click.option('--staging', type=click.BOOL, is_flag=True, help='Target staging')
@click.option('--production', type=click.BOOL, is_flag=True, help='Target production')
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, help='Verbose output')
def set(env_vars, staging, production, verbose):
  """Set environment variables - each of {ENV_VARS} must be in of form 'KEY=VALUE'"""
  set_verbosity(verbose)
  context = select_context(staging, production)
  hokusai.set_env(context, env_vars)


@env.command(context_settings=CONTEXT_SETTINGS)
@click.argument('env_vars', type=click.STRING, nargs=-1)
@click.option('--staging', type=click.BOOL, is_flag=True, help='Target staging')
@click.option('--production', type=click.BOOL, is_flag=True, help='Target production')
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, help='Verbose output')
def unset(env_vars, staging, production, verbose):
  """Unset environment variables - each of {ENV_VARS} must be of the form 'KEY'"""
  set_verbosity(verbose)
  context = select_context(staging, production)
  hokusai.unset_env(context, env_vars)


@env.command(context_settings=CONTEXT_SETTINGS)
@click.option('--staging', type=click.BOOL, is_flag=True, help='Target staging')
@click.option('--production', type=click.BOOL, is_flag=True, help='Target production')
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, help='Verbose output')
def delete(staging, production, verbose):
  """Delete the Kubernetes configmap object `{project_name}-environment`"""
  set_verbosity(verbose)
  context = select_context(staging, production)
  hokusai.delete_env(context)
