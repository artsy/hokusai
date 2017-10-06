import os

import click

import hokusai

from hokusai.cli.base import cli
from hokusai.lib.common import set_verbosity, select_context, CONTEXT_SETTINGS

@cli.group()
def local(context_settings=CONTEXT_SETTINGS):
  """Interact with your local project and Docker engine"""
  pass

@local.command(context_settings=CONTEXT_SETTINGS)
@click.option('--aws-account-id', type=click.STRING, required=True, envvar='AWS_ACCOUNT_ID', help='Your AWS account ID (default: $AWS_ACCOUNT_ID)')
@click.option('--project-type', type=click.Choice(['ruby-rack', 'ruby-rails', 'nodejs', 'elixir', 'python-wsgi']), required=True, help='The type of project')
@click.option('--project-name', type=click.STRING, default=os.path.basename(os.getcwd()), help='The project name (default: name of current directory)')
@click.option('--aws-ecr-region', type=click.STRING, default='us-east-1', envvar='AWS_DEFAULT_REGION', help='Your AWS ECR region (default: $AWS_DEFAULT_REGION or \'us-east-1\')')
@click.option('--port', type=click.INT, default=80, help='The port of the service (default: 80)')
def setup(aws_account_id, project_type, project_name, aws_ecr_region, port):
  """
  Set up Hokusai for the current project
  """
  hokusai.setup(aws_account_id, project_type, project_name, aws_ecr_region, port)

@local.command(context_settings=CONTEXT_SETTINGS)
def build():
  """
  Build the Docker image defined in ./hokusai/common.yml
  """
  hokusai.build()

@local.command(context_settings=CONTEXT_SETTINGS)
@click.option('-b', '--build', type=click.BOOL, is_flag=True, help='Force rebuild the docker image before running the test suite')
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, help='Verbose output')
def test(build, verbose):
  """Boot the test stack and run the test suite

  Return the exit code of the container with the name 'project-name' in hokusai/config.yml"""
  set_verbosity(verbose)
  hokusai.test(build)

@local.command(context_settings=CONTEXT_SETTINGS)
@click.option('--tag', type=click.STRING, help='The tag to push (default: the value of `git rev-parse HEAD`)')
@click.option('--force', type=click.BOOL, is_flag=True, help='Push even if working directory is not clean')
@click.option('--overwrite', type=click.BOOL, is_flag=True, help='Push even if the tag already exists')
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, help='Verbose output')
def push(tag, force, overwrite, verbose):
  """
  Build and push an image to the project's remote repo tagged as the git SHA1 of HEAD
  """
  set_verbosity(verbose)
  hokusai.push(tag, force, overwrite)
