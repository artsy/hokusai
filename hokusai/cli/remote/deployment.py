import click

import hokusai
from hokusai.cli.remote import remote
from hokusai.lib.common import set_verbosity, select_context, CONTEXT_SETTINGS

@remote.group()
def deployment(context_settings=CONTEXT_SETTINGS):
  """Interact with the project's' remote Kubernetes deployment(s)"""
  pass

@deployment.command(context_settings=CONTEXT_SETTINGS)
@click.argument('tag', type=click.STRING)
@click.option('--migration', type=click.STRING, help='Run a migration before deploying')
@click.option('--constraint', type=click.STRING, multiple=True, help='Constrain migration and deploy hooks to run on nodes matching labels in the form of "key=value"')
@click.option('--staging', type=click.BOOL, is_flag=True, help='Target staging')
@click.option('--production', type=click.BOOL, is_flag=True, help='Target production')
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, help='Verbose output')
def update(tag, migration, constraint, staging, production, verbose):
  """Update the project's deployment(s) for a given remote environment to reference
  the given image tag and update the tag (staging/production)
  to reference the same image"""
  set_verbosity(verbose)
  context = select_context(staging, production)
  hokusai.update(context, tag, migration, constraint)


@deployment.command(context_settings=CONTEXT_SETTINGS)
@click.option('--staging', type=click.BOOL, is_flag=True, help='Target staging')
@click.option('--production', type=click.BOOL, is_flag=True, help='Target production')
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, help='Verbose output')
def history(staging, production, verbose):
  """Print the project's deployment history in terms of revision number,
  creation time, container name and image tag for a given environment"""
  set_verbosity(verbose)
  context = select_context(staging, production)
  hokusai.history(context)


@deployment.command(context_settings=CONTEXT_SETTINGS)
@click.option('--staging', type=click.BOOL, is_flag=True, help='Target staging')
@click.option('--production', type=click.BOOL, is_flag=True, help='Target production')
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, help='Verbose output')
def refresh(staging, production, verbose):
  """Refresh the project's deployment(s) by recreating the currently running containers"""
  set_verbosity(verbose)
  context = select_context(staging, production)
  hokusai.refresh(context)


@deployment.command(context_settings=CONTEXT_SETTINGS)
@click.option('--migration', type=click.STRING, help='Run a migration before deploying')
@click.option('--constraint', type=click.STRING, multiple=True, help='Constrain migration and deploy hooks to run on nodes matching labels in the form of "key=value"')
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, help='Verbose output')
def promote(migration, constraint, verbose):
  """Update the project's deployment(s) on production with the image tag
  currently deployed on staging and update the production tag
  to reference the same image"""
  set_verbosity(verbose)
  hokusai.promote(migration, constraint)
