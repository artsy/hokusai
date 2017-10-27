import click

import hokusai

from hokusai.cli.base import base
from hokusai.lib.common import set_verbosity, CONTEXT_SETTINGS

@base.group()
def pipeline(context_settings=CONTEXT_SETTINGS):
  """Interact with the project's' staging -> production pipeline"""
  pass


@pipeline.command(context_settings=CONTEXT_SETTINGS)
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, help='Verbose output')
def gitdiff(verbose):
  """Print a git diff between the tag currently deployed on production
  and the tag currently deployed on staging"""
  set_verbosity(verbose)
  hokusai.gitdiff()


@pipeline.command(context_settings=CONTEXT_SETTINGS)
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, help='Verbose output')
def gitlog(verbose):
  """Print a git log between the tag currently deployed on production
  and the tag currently deployed on staging"""
  set_verbosity(verbose)
  hokusai.gitlog()


@pipeline.command(context_settings=CONTEXT_SETTINGS)
@click.option('--migration', type=click.STRING, help='Run a migration before deploying')
@click.option('--constraint', type=click.STRING, multiple=True, help='Constrain migration and deploy hooks to run on nodes matching labels in the form of "key=value"')
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, help='Verbose output')
def promote(migration, constraint, verbose):
  """Update the project's deployment(s) on production with the image tag
  currently deployed on staging and update the production tag
  to reference the same image"""
  set_verbosity(verbose)
  hokusai.promote(migration, constraint)
