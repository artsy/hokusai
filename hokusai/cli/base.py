import os

import click
from click_repl import repl

import hokusai
from hokusai.lib.command import command
from hokusai.lib.common import set_verbosity, CONTEXT_SETTINGS

@click.group()
def base(context_settings=CONTEXT_SETTINGS):
  """Hokusai is a CLI for managing application deployments on Kubernetes"""
  pass

@base.command(context_settings=CONTEXT_SETTINGS)
@click.pass_context
def tree(ctx):
  """Print a tree of available commands"""
  hokusai.print_command_tree(ctx.find_root().command)

@base.command(context_settings=CONTEXT_SETTINGS)
def console():
    """Start an interactive console session"""
    repl(click.get_current_context())


@base.command(context_settings=CONTEXT_SETTINGS)
@click.option('--kubeconfig-dir', type=click.STRING, default=None, help='Directory to install kubeconfig into. The kubeconfig file will be named "config". (default: None)')
@click.option('--kubectl-dir', type=click.STRING, default=None, help='Directory to install kubectl into. The executable will be named "kubectl". (default: None)')
@click.option('--skip-kubeconfig', type=click.BOOL, is_flag=True, help='Skip kubeconfig install.')
@click.option('--skip-kubectl', type=click.BOOL, is_flag=True, help='Skip kubectl install.')
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, help='Verbose output.')
def configure(kubeconfig_dir, kubectl_dir, skip_kubeconfig, skip_kubectl, verbose):
  """Pull new Hokusai global config, download kubeconfig, install kubectl, save final global config to ~/.hokusai.yml"""
  set_verbosity(verbose)
  command(
    hokusai.hokusai_configure,
    kubeconfig_dir,
    kubectl_dir,
    skip_kubeconfig,
    skip_kubectl,
    config_check=False
  )


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
  command(
    hokusai.setup,
    project_name,
    template_remote,
    template_dir,
    var,
    allow_missing_vars,
    config_check=False
  )


@base.command(context_settings=CONTEXT_SETTINGS)
@click.option('-f', '--filename', type=click.STRING, help='Use the given docker-compose Yaml file (default: ./hokusai/build.yml)')
@click.option('-v', '--verbose', type=click.BOOL, is_flag=True, help='Verbose output')
def build(filename, verbose):
  """Build the Docker image defined in ./hokusai/build.yml"""
  set_verbosity(verbose)
  command(
    hokusai.build,
    filename
  )


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
  command(
    hokusai.test,
    build,
    cleanup,
    filename,
    service_name
  )


@base.command(context_settings=CONTEXT_SETTINGS)
def check():
  """Check Hokusai dependencies and configuration"""
  command(
    hokusai.check
  )


@base.command(context_settings=CONTEXT_SETTINGS)
def version():
  """Print Hokusai's version and exit"""
  command(
    hokusai.version,
    config_check=False
  )

if __name__ == '__main__':
  base(obj={})
