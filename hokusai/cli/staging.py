import click

import hokusai

from hokusai.cli.base import base
from hokusai.lib.common import set_verbosity, CONTEXT_SETTINGS

KUBE_CONTEXT = 'staging'

@base.group()
def staging(context_settings=CONTEXT_SETTINGS):
  """Interact with the staging Kubernetes environment
  defined by the `staging` context in `~/.kube/config` and the 
  Kubernetes resources in `./hokusai/staging.yml`"""
  pass

@staging.command(context_settings=CONTEXT_SETTINGS)
@click.option('-f', '--filename', type=click.STRING, help='Use the given Kubernetes Yaml file (default ./hokusai/staging.yml)')
@click.option('-e', '--environment', type=click.STRING, multiple=True, help='Create stack with the given environment variables (only applies if --filename is not supplied)')
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, help='Verbose output')
def create(filename, environment, verbose):
  """Create the Kubernetes resources defined in ./hokusai/staging.yml"""
  set_verbosity(verbose)
  hokusai.k8s_create(KUBE_CONTEXT, filename=filename, environment=environment)


@staging.command(context_settings=CONTEXT_SETTINGS)
@click.option('-f', '--filename', type=click.STRING, help='Use the given Kubernetes Yaml file (default ./hokusai/staging.yml)')
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, help='Verbose output')
def delete(filename, verbose):
  """Delete the Kubernetes resources defined in ./hokusai/staging.yml"""
  set_verbosity(verbose)
  hokusai.k8s_delete(KUBE_CONTEXT, filename=filename)


@staging.command(context_settings=CONTEXT_SETTINGS)
@click.option('--check-branch', type=click.STRING, default="master", help='Check branch before updating (default: master)')
@click.option('--check-remote', type=click.STRING, help='Check remotes before updating (otherwise check all remotes)')
@click.option('--skip-checks', type=click.BOOL, is_flag=True, help='Skip all checks and update configuration recklessly')
@click.option('-f', '--filename', type=click.STRING, help='Use the given Kubernetes Yaml file (default ./hokusai/staging.yml)')
@click.option('--dry-run', type=click.BOOL, is_flag=True, help='Perform a dry run of the configuration update')
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, help='Verbose output')
def update(check_branch, check_remote, skip_checks, filename, dry_run, verbose):
  """Update the Kubernetes resources defined in ./hokusai/staging.yml"""
  set_verbosity(verbose)
  hokusai.k8s_update(KUBE_CONTEXT, check_branch=check_branch,
                      check_remote=check_remote, skip_checks=skip_checks,
                      filename=filename, dry_run=dry_run)


@staging.command(context_settings=CONTEXT_SETTINGS)
@click.option('--resources/--no-resources', default=True, help='Print Kubernetes API objects defined in ./hokusai/staging.yml (default: true)')
@click.option('--pods/--no-pods', default=True, help='Print pods (default: true)')
@click.option('--describe', type=click.BOOL, is_flag=True, help="Print 'kubectl describe' output for resources and pods")
@click.option('--top', type=click.BOOL, is_flag=True, help='Print top pods')
@click.option('-f', '--filename', type=click.STRING, help='Use the given Kubernetes Yaml file (default ./hokusai/staging.yml)')
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, help='Verbose output')
def status(resources, pods, describe, top, filename, verbose):
  """Print Kubernetes resources in the staging context"""
  set_verbosity(verbose)
  hokusai.k8s_status(KUBE_CONTEXT, resources, pods, describe, top, filename=filename)


@staging.command(context_settings=CONTEXT_SETTINGS)
@click.argument('command', type=click.STRING)
@click.option('--tty', type=click.BOOL, is_flag=True, help='Attach the terminal')
@click.option('--tag', type=click.STRING, help='The image tag to run (defaults to "staging")')
@click.option('--env', type=click.STRING, multiple=True, help='Environment variables in the form of "KEY=VALUE"')
@click.option('--constraint', type=click.STRING, multiple=True, help='Constrain command to run on nodes matching labels in the form of "key=value"')
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, help='Verbose output')
def run(command, tty, tag, env, constraint, verbose):
  """Launch a new container and run a command"""
  set_verbosity(verbose)
  hokusai.run(KUBE_CONTEXT, command, tty, tag, env, constraint)


@staging.command(context_settings=CONTEXT_SETTINGS)
@click.option('-s', '--timestamps', type=click.BOOL, is_flag=True, help='Include timestamps')
@click.option('-f', '--follow', type=click.BOOL, is_flag=True, help='Follow logs')
@click.option('-t', '--tail', type=click.INT, help="Number of lines of recent logs to display")
@click.option('-p', '--previous', type=click.BOOL, is_flag=True, help='Get from the previous run of the Pod container(s)')
@click.option('-l', '--label', type=click.STRING, multiple=True, help='Filter pods by additional label selectors in the form of "key=value"')
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, help='Verbose output')
def logs(timestamps, follow, tail, previous, label, verbose):
  """Get container logs"""
  set_verbosity(verbose)
  hokusai.logs(KUBE_CONTEXT, timestamps, follow, tail, previous, label)

@staging.command(context_settings=CONTEXT_SETTINGS)
@click.argument('tag', type=click.STRING)
@click.option('--migration', type=click.STRING, help='Run a migration before deploying')
@click.option('--constraint', type=click.STRING, multiple=True, help='Constrain migration and deploy hooks to run on nodes matching labels in the form of "key=value"')
@click.option('--git-remote', type=click.STRING, help='Push deployment tags to git remote')
@click.option('-t', '--timeout', type=click.INT, default=600, help="Timeout deployment rollout after N seconds (default 600)")
@click.option('-u', '--update-config', type=click.BOOL, is_flag=True, help='Also update Kubernetes config')
@click.option('-f', '--filename', type=click.STRING, help='If updating config, use the Kubernetes Yaml file in the ./hokusai directory (default staging.yml)')
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, help='Verbose output')
def deploy(tag, migration, constraint, git_remote, timeout, update_config, filename, verbose):
  """Update the project's deployment(s) to reference
  the given image tag and update the tag staging
  to reference the same image"""
  set_verbosity(verbose)
  hokusai.update(KUBE_CONTEXT, tag, migration, constraint, git_remote, timeout, update_config=update_config, filename=filename)


@staging.command(context_settings=CONTEXT_SETTINGS)
@click.option('-d', '--deployment', type=click.STRING, help='Only refresh the given deployment')
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, help='Verbose output')
def refresh(deployment, verbose):
  """Refresh the project's deployment(s) by recreating the currently running containers"""
  set_verbosity(verbose)
  hokusai.refresh(KUBE_CONTEXT, deployment)


@staging.command(context_settings=CONTEXT_SETTINGS)
@click.option('-d', '--deployment', type=click.STRING, help='Only refresh the given deployment')
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, help='Verbose output')
def restart(deployment, verbose):
  """Alias for 'refresh'"""
  set_verbosity(verbose)
  hokusai.refresh(KUBE_CONTEXT, deployment)


@staging.group()
def env(context_settings=CONTEXT_SETTINGS):
  """Interact with the runtime environment for the application"""
  pass


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
