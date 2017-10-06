import os

import click

import hokusai
from hokusai.lib.common import CONTEXT_SETTINGS

@click.group()
def cli(context_settings=CONTEXT_SETTINGS):
  """Hokusai is a CLI for managing application deployments on Kubernetes"""
  pass


@cli.command(context_settings=CONTEXT_SETTINGS)
def version():
  """Print Hokusai's version and exit"""
  hokusai.version()


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.option('--kubectl-version', type=click.STRING, required=True, help='The version of kubectl to install')
@click.option('--s3-bucket', type=click.STRING, required=True, help="The S3 bucket name containing your org's kubectl config file")
@click.option('--s3-key', type=click.STRING, required=True, help="The S3 key of your org's kubectl config file")
@click.option('--platform', type=click.Choice(['darwin', 'linux']), default='darwin', help='The platform OS (default: darwin)')
@click.option('--install-to', type=click.STRING, default='/usr/local/bin', help='Install kubectl to (default: /usr/local/bin)')
@click.option('--install-config-to', type=click.STRING, default=os.path.join(os.environ.get('HOME'), '.kube'), help='Install kubectl config to (default: ~/.kube)')
def configure(kubectl_version, s3_bucket, s3_key, platform, install_to, install_config_to):
  """Install and configure kubectl"""
  hokusai.configure(kubectl_version, s3_bucket, s3_key, platform, install_to, install_config_to)

@cli.command(context_settings=CONTEXT_SETTINGS)
def check():
  """Check Hokusai dependencies and configuration"""
  hokusai.check()
