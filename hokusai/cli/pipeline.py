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
@click.option('--org-name', type=click.STRING, required=True, help='Name of the (github) organization')
@click.option('--git-compare-link', type=click.STRING, help='Python formatted string input that gets org name, project name and 2 diff sha1s, example: https://github.com/%s/%s/compare/%s...%s', default="https://github.com/%s/%s/compare/%s...%s")
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, help='Verbose output')
def gitcompare(org_name, git_compare_link, verbose):
  """Prints a git compare link between the tag currently deployed on production
  and the tag currently deployed on staging"""
  set_verbosity(verbose)
  hokusai.gitcompare(org_name, git_compare_link)


@pipeline.command(context_settings=CONTEXT_SETTINGS)
@click.option('--migration', type=click.STRING, help='Run a migration before deploying')
@click.option('--constraint', type=click.STRING, multiple=True, help='Constrain migration and deploy hooks to run on nodes matching labels in the form of "key=value"')
@click.option('--git-remote', type=click.STRING, help='Push deployment tags to git remote')
@click.option('-t', '--timeout', type=click.INT, default=600, help="Timeout deployment rollout after N seconds (default 600)")
@click.option('-u', '--update-config', type=click.BOOL, is_flag=True, help='Also update Kubernetes config')
@click.option('-f', '--filename', type=click.STRING, help='If updating config, use the Kubernetes Yaml file in the ./hokusai directory (default production.yml)')
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, help='Verbose output')
def promote(migration, constraint, git_remote, timeout, update_config, filename, verbose):
  """Update the project's deployment(s) on production with the image tag
  currently deployed on staging and update the production tag
  to reference the same image"""
  set_verbosity(verbose)
  hokusai.promote(migration, constraint, git_remote, timeout, update_config=update_config, filename=filename)
