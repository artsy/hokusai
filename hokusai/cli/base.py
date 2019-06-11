import os

import click
from click_repl import repl

import hokusai
from hokusai.lib.common import set_verbosity, CONTEXT_SETTINGS

@click.group()
def base(context_settings=CONTEXT_SETTINGS):
  """Hokusai is a CLI for managing application deployments on Kubernetes"""
  pass


@base.command(context_settings=CONTEXT_SETTINGS)
def console():
    """Start an interactive console session"""
    repl(click.get_current_context())


@base.command(context_settings=CONTEXT_SETTINGS)
@click.option('--kubectl-version', type=click.STRING, required=False, help='The version of kubectl to install')
@click.option('--s3-bucket', type=click.STRING, required=False, help="The S3 bucket name containing your org's kubectl config file")
@click.option('--s3-key', type=click.STRING, required=False, help="The S3 key of your org's kubectl config file")
@click.option('--config_file', type=click.STRING, required=False, help="Your org's kubectl config file")
@click.option('--platform', type=click.Choice(['darwin', 'linux']), default='darwin', help='The platform OS (default: darwin)')
@click.option('--install-to', type=click.STRING, default='/usr/local/bin', help='Install kubectl to (default: /usr/local/bin)')
@click.option('--install-config-to', type=click.STRING, default=os.path.join(os.environ.get('HOME'), '.kube'), help='Install kubectl config to (default: ~/.kube)')
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, help='Verbose output')
def configure(kubectl_version, s3_bucket, s3_key, config_file, platform, install_to, install_config_to, verbose):
  """Install and configure kubectl"""
  set_verbosity(verbose)
  hokusai.configure(kubectl_version, s3_bucket, s3_key, config_file, install_to, install_config_to)


@base.command(context_settings=CONTEXT_SETTINGS)
@click.option('--project-name', type=click.STRING, default=os.path.basename(hokusai.CWD), help='The project name (default: name of current directory)')
@click.option('--template-remote', type=click.STRING, help='Git remote of templates to use - you can specify a branch via <git-remote>#<branch>')
@click.option('--template-dir', type=click.STRING, help='Directory of templates to use - can be used with --template-remote')
@click.option('--var', type=click.STRING, multiple=True, help='Extra variables to render Jinja templates in the form of key=value')
@click.option('--allow-missing-vars', is_flag=True, help='Do not fail on undefined template vars')
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, help='Verbose output')
def setup(project_name, template_remote, template_dir, var, allow_missing_vars, verbose):
  """Set up Hokusai for the current project"""
  set_verbosity(verbose)
  hokusai.setup(project_name, template_remote, template_dir, var, allow_missing_vars)


@base.command(context_settings=CONTEXT_SETTINGS)
@click.option('-f', '--filename', type=click.STRING, help='Use the given docker-compose Yaml file (default: ./hokusai/build.yml)')
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, help='Verbose output')
def build(filename, verbose):
  """Build the Docker image defined in ./hokusai/build.yml"""
  set_verbosity(verbose)
  hokusai.build(filename)


@base.command(context_settings=CONTEXT_SETTINGS)
@click.option('--build/--no-build', default=True, help='Force a build of the :latest image before running the test suite (default: true)')
@click.option('--cleanup/--no-cleanup', default=False, help='Remove containers on exit / error (default: False)')
@click.option('-f', '--filename', type=click.STRING, help='Use the given docker-compose Yaml file (default: ./hokusai/test.yml)')
@click.option('--service-name', type=click.STRING, help="The service name to treat as the test container (default: the value of 'project-name' in `hokusai/config.yml`)")
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, help='Verbose output')
def test(build, cleanup, filename, service_name, verbose):
  """Boot the docker-compose test environment defined by `./hokusai/test.yml` and run the test suite

  Return the exit code of the container with the name 'project-name' in `hokusai/config.yml`"""
  set_verbosity(verbose)
  hokusai.test(build, cleanup, filename, service_name)


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
