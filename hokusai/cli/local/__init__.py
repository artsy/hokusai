import os

import click

import hokusai

from hokusai.cli.base import base
from hokusai.lib.common import set_verbosity, select_context, CONTEXT_SETTINGS

@base.group()
def local(context_settings=CONTEXT_SETTINGS):
  """Interact with your local project and Docker engine"""
  pass


@local.command(context_settings=CONTEXT_SETTINGS)
def build():
  """Build the Docker image defined in ./hokusai/common.yml"""
  hokusai.build()


@local.command(context_settings=CONTEXT_SETTINGS)
@click.option('-b', '--build', type=click.BOOL, is_flag=True, help='Force rebuild the docker image before running the test suite')
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, help='Verbose output')
def test(build, verbose):
  """Boot the test environment defined in ./hokusai/test.yml and run the test suite

  Return the exit code of the container with the name 'project-name' in hokusai/config.yml"""
  set_verbosity(verbose)
  hokusai.test(build)


@local.command(context_settings=CONTEXT_SETTINGS)
@click.option('--tag', type=click.STRING, help='The tag to push (default: the value of `git rev-parse HEAD`)')
@click.option('--force', type=click.BOOL, is_flag=True, help='Push even if working directory is not clean')
@click.option('--overwrite', type=click.BOOL, is_flag=True, help='Push even if the tag already exists')
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, help='Verbose output')
def push(tag, force, overwrite, verbose):
  """Build and push an image to the project's remote repo tagged as the git SHA1 of HEAD"""
  set_verbosity(verbose)
  hokusai.push(tag, force, overwrite)
