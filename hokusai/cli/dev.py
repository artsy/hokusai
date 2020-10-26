import click

import hokusai

from hokusai.cli.base import base
from hokusai.lib.common import set_verbosity, CONTEXT_SETTINGS
from hokusai.lib.config import config

@base.group()
def dev(context_settings=CONTEXT_SETTINGS):
  """Interact with docker-compose development environment
  defined by ./hokusai/development.yml"""
  pass


@dev.command(context_settings=CONTEXT_SETTINGS)
@click.option('--build/--no-build', default=True, help='Force a build of the :latest image before starting (default: true)')
@click.option('-d', '--detach', type=click.BOOL, is_flag=True, help="Run containers in the background")
@click.option('-f', '--filename', type=click.STRING, help='Use the given docker-compose Yaml file (default ./hokusai/development.yml.j2)')
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, help='Verbose output')
def start(build, detach, filename, verbose):
  """Start the development environment defined in ./hokusai/development.yml"""
  set_verbosity(verbose)
  hokusai.dev_start(build, detach, filename)


@dev.command(context_settings=CONTEXT_SETTINGS)
@click.option('-f', '--filename', type=click.STRING, help='Use the given docker-compose Yaml file (default ./hokusai/development.yml.j2)')
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, help='Verbose output')
def stop(filename, verbose):
  """Stop the development environment defined in ./hokusai/development.yml"""
  set_verbosity(verbose)
  hokusai.dev_stop(filename)


@dev.command(context_settings=CONTEXT_SETTINGS)
@click.option('-f', '--filename', type=click.STRING, help='Use the given docker-compose Yaml file (default ./hokusai/development.yml.j2)')
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, help='Verbose output')
def status(filename, verbose):
  """Print the status of the development environment defined in ./hokusai/development.yml"""
  set_verbosity(verbose)
  hokusai.dev_status(filename)


@dev.command(context_settings=CONTEXT_SETTINGS)
@click.option('-f', '--follow', type=click.BOOL, is_flag=True, help="Follow output")
@click.option('-t', '--tail', type=click.INT, help="Number of lines of recent logs to display")
@click.option('-fi', '--filename', type=click.STRING, help='Use the docker-compose Yaml file (default ./hokusai/development.yml.j2)')
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, help='Verbose output')
def logs(follow, tail, filename, verbose):
  """Print logs from the development environment defined in ./hokusai/development.yml"""
  set_verbosity(verbose)
  hokusai.dev_logs(follow, tail, filename)


@dev.command(context_settings=CONTEXT_SETTINGS)
@click.argument('command')
@click.option('--service-name', type=click.STRING, help="The service name to launch the container as (default: the name 'project-name' in `hokusai/config.yml`)")
@click.option('--stop', type=click.BOOL, is_flag=True, help='Stop all services after running the command')
@click.option('-f', '--filename', type=click.STRING, help='Use the given docker-compose Yaml file (default ./hokusai/development.yml.j2)')
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, help='Verbose output')
def run(command, service_name, stop, filename, verbose):
  """Run a command in a new container in the development environment defined in ./hokusai/development.yml"""
  set_verbosity(verbose)
  hokusai.dev_run(command, service_name, stop, filename)


@dev.command(context_settings=CONTEXT_SETTINGS)
@click.option('-f', '--filename', type=click.STRING, help='Use the given docker-compose Yaml file (default ./hokusai/development.yml.j2)')
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, help='Verbose output')
def clean(filename, verbose):
  """Stop and remove all containers in the development environment defined in ./hokusai/development.yml.j2"""
  set_verbosity(verbose)
  hokusai.dev_clean(filename)
