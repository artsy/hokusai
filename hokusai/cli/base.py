import os

import click

import hokusai
from hokusai.lib.common import set_verbosity, CONTEXT_SETTINGS

@click.group()
def base(context_settings=CONTEXT_SETTINGS):
  """Hokusai is a CLI for managing application deployments on Kubernetes"""
  pass


@base.command(context_settings=CONTEXT_SETTINGS)
@click.option('--kubectl-version', type=click.STRING, required=False, help='The version of kubectl to install')
@click.option('--s3-bucket', type=click.STRING, required=False, help="The S3 bucket name containing your org's kubectl config file")
@click.option('--s3-key', type=click.STRING, required=False, help="The S3 key of your org's kubectl config file")
@click.option('--config_file', type=click.STRING, required=False, help="Your org's kubectl config file")
@click.option('--platform', type=click.Choice(['darwin', 'linux']), default='darwin', help='The platform OS (default: darwin)')
@click.option('--install-to', type=click.STRING, default='/usr/local/bin', help='Install kubectl to (default: /usr/local/bin)')
@click.option('--install-config-to', type=click.STRING, default=os.path.join(os.environ.get('HOME'), '.kube'), help='Install kubectl config to (default: ~/.kube)')
def configure(kubectl_version, s3_bucket, s3_key, config_file, platform, install_to, install_config_to):
  """Install and configure kubectl"""
  hokusai.configure(kubectl_version, s3_bucket, s3_key, config_file, platform, install_to, install_config_to)


@base.command(context_settings=CONTEXT_SETTINGS)
@click.option('--project-type', type=click.Choice(['ruby-rack', 'ruby-rails', 'nodejs', 'elixir', 'python-wsgi']), required=True, help='The type of project')
@click.option('--project-name', type=click.STRING, default=os.path.basename(os.getcwd()), help='The project name (default: name of current directory)')
@click.option('--port', type=click.INT, default=8080, help='The port of the service (default: 8080)')
@click.option('--internal', type=click.BOOL, is_flag=True, help='Create an internal Kubernetes service definition')
@click.option('--template-dir', type=click.STRING, default="", help='Directory of templates to use.')
def setup(project_type, project_name, port, internal, template_dir):
  """Set up Hokusai for the current project"""
  hokusai.setup(project_type, project_name, port, internal, template_dir)


@base.command(context_settings=CONTEXT_SETTINGS)
def build():
  """Build the Docker image defined in ./hokusai/common.yml"""
  hokusai.build()


@base.command(context_settings=CONTEXT_SETTINGS)
@click.option('--build/--no-build', default=True, help='Force a build of the :latest image before running the test suite (default: true)')
@click.option('--cleanup/--no-cleanup', default=False, help='Remove containers on exit / error (default: False)')
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, help='Verbose output')
def test(build, cleanup, verbose):
  """Boot the docker-compose test environment defined by `./hokusai/test.yml` and run the test suite

  Return the exit code of the container with the name 'project-name' in `hokusai/config.yml`"""
  set_verbosity(verbose)
  hokusai.test(build, cleanup)


@base.command(context_settings=CONTEXT_SETTINGS)
def check():
  """Check Hokusai dependencies and configuration"""
  hokusai.check()


@base.command(context_settings=CONTEXT_SETTINGS)
def version():
  """Print Hokusai's version and exit"""
  hokusai.version()

if __name__ == '__main__':
  base(obj={})
