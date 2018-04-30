import click

import hokusai

from hokusai.cli.base import base
from hokusai.lib.common import set_verbosity, CONTEXT_SETTINGS

KUBE_CONTEXT = 'production'

@base.group()
def production(context_settings=CONTEXT_SETTINGS):
  """Interact with the production Kubernetes environment
  defined by the `production` context in `~/.kube/config` and the 
  Kubernetes resources in `./hokusai/production.yml`"""
  pass

@production.command(context_settings=CONTEXT_SETTINGS)
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, help='Verbose output')
def create(verbose):
  """Create the Kubernetes resources defined in ./hokusai/production.yml"""
  set_verbosity(verbose)
  hokusai.k8s_create(KUBE_CONTEXT)


@production.command(context_settings=CONTEXT_SETTINGS)
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, help='Verbose output')
def delete(verbose):
  """Delete the Kubernetes resources defined in ./hokusai/production.yml"""
  set_verbosity(verbose)
  hokusai.k8s_delete(KUBE_CONTEXT)


@production.command(context_settings=CONTEXT_SETTINGS)
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, help='Verbose output')
def update(verbose):
  """Update the Kubernetes resources defined in ./hokusai/production.yml"""
  set_verbosity(verbose)
  hokusai.k8s_update(KUBE_CONTEXT)


@production.command(context_settings=CONTEXT_SETTINGS)
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, help='Verbose output')
def status(verbose):
  """Print the Kubernetes resources status defined in ./hokusai/production.yml"""
  set_verbosity(verbose)
  hokusai.k8s_status(KUBE_CONTEXT)


@production.command(context_settings=CONTEXT_SETTINGS)
@click.argument('command', type=click.STRING)
@click.option('--tty', type=click.BOOL, is_flag=True, help='Attach the terminal')
@click.option('--tag', type=click.STRING, help='The image tag to run (defaults to "production")')
@click.option('--env', type=click.STRING, multiple=True, help='Environment variables in the form of "KEY=VALUE"')
@click.option('--constraint', type=click.STRING, multiple=True, help='Constrain command to run on nodes matching labels in the form of "key=value"')
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, help='Verbose output')
def run(command, tty, tag, env, constraint, verbose):
  """Launch a new container and run a command"""
  set_verbosity(verbose)
  hokusai.run(KUBE_CONTEXT, command, tty, tag, env, constraint)


@production.command(context_settings=CONTEXT_SETTINGS)
@click.option('-t', '--timestamps', type=click.BOOL, is_flag=True, help='Include timestamps')
@click.option('-f', '--follow', type=click.BOOL, is_flag=True, help='Follow logs')
@click.option('-t', '--tail', type=click.INT, help="Number of lines of recent logs to display")
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, help='Verbose output')
def logs(timestamps, follow, tail, verbose):
  """Get container logs"""
  set_verbosity(verbose)
  hokusai.logs(KUBE_CONTEXT, timestamps, follow, tail)

@production.command(context_settings=CONTEXT_SETTINGS)
@click.argument('tag', type=click.STRING)
@click.option('--migration', type=click.STRING, help='Run a migration before deploying')
@click.option('--constraint', type=click.STRING, multiple=True, help='Constrain migration and deploy hooks to run on nodes matching labels in the form of "key=value"')
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, help='Verbose output')
def deploy(tag, migration, constraint, verbose):
  """Update the project's deployment(s) to reference
  the given image tag and update the tag production
  to reference the same image"""
  set_verbosity(verbose)
  hokusai.update(KUBE_CONTEXT, tag, migration, constraint)


@production.command(context_settings=CONTEXT_SETTINGS)
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, help='Verbose output')
def history(verbose):
  """Print the project's deployment history in terms of revision number,
  creation time, container name and image tag"""
  set_verbosity(verbose)
  hokusai.history(KUBE_CONTEXT)


@production.command(context_settings=CONTEXT_SETTINGS)
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, help='Verbose output')
def refresh(verbose):
  """Refresh the project's deployment(s) by recreating the currently running containers"""
  set_verbosity(verbose)
  hokusai.refresh(KUBE_CONTEXT)


@production.group()
def env(context_settings=CONTEXT_SETTINGS):
  """Interact with the runtime environment for the application"""
  pass


@env.command(context_settings=CONTEXT_SETTINGS)
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, help='Verbose output')
def create(verbose):
  """Create the Kubernetes configmap object `{project_name}-environment`"""
  set_verbosity(verbose)
  hokusai.create_env(KUBE_CONTEXT)


@env.command(context_settings=CONTEXT_SETTINGS)
@click.argument('env_vars', type=click.STRING, nargs=-1)
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, help='Verbose output')
def get(env_vars, verbose):
  """Print environment variables stored on the Kubernetes server"""
  set_verbosity(verbose)
  hokusai.get_env(KUBE_CONTEXT, env_vars)


@env.command(context_settings=CONTEXT_SETTINGS)
@click.argument('env_vars', type=click.STRING, nargs=-1)
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, help='Verbose output')
def set(env_vars, verbose):
  """Set environment variables - each of {ENV_VARS} must be in of form 'KEY=VALUE'"""
  set_verbosity(verbose)
  hokusai.set_env(KUBE_CONTEXT, env_vars)


@env.command(context_settings=CONTEXT_SETTINGS)
@click.argument('env_vars', type=click.STRING, nargs=-1)
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, help='Verbose output')
def unset(env_vars, verbose):
  """Unset environment variables - each of {ENV_VARS} must be of the form 'KEY'"""
  set_verbosity(verbose)
  hokusai.unset_env(KUBE_CONTEXT, env_vars)


@env.command(context_settings=CONTEXT_SETTINGS)
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, help='Verbose output')
def delete(verbose):
  """Delete the Kubernetes configmap object `{project_name}-environment`"""
  set_verbosity(verbose)
  hokusai.delete_env(KUBE_CONTEXT)
