import os

import click

import hokusai
from hokusai.lib.common import CONTEXT_SETTINGS

@click.group()
def base(context_settings=CONTEXT_SETTINGS):
  """Hokusai is a CLI for managing application deployments on Kubernetes"""
  pass


@base.command(context_settings=CONTEXT_SETTINGS)
@click.option('--kubectl-version', type=click.STRING, required=True, help='The version of kubectl to install')
@click.option('--s3-bucket', type=click.STRING, required=True, help="The S3 bucket name containing your org's kubectl config file")
@click.option('--s3-key', type=click.STRING, required=True, help="The S3 key of your org's kubectl config file")
@click.option('--platform', type=click.Choice(['darwin', 'linux']), default='darwin', help='The platform OS (default: darwin)')
@click.option('--install-to', type=click.STRING, default='/usr/local/bin', help='Install kubectl to (default: /usr/local/bin)')
@click.option('--install-config-to', type=click.STRING, default=os.path.join(os.environ.get('HOME'), '.kube'), help='Install kubectl config to (default: ~/.kube)')
def configure(kubectl_version, s3_bucket, s3_key, platform, install_to, install_config_to):
  """Install and configure kubectl"""
  hokusai.configure(kubectl_version, s3_bucket, s3_key, platform, install_to, install_config_to)


@base.command(context_settings=CONTEXT_SETTINGS)
@click.option('--aws-account-id', type=click.STRING, required=True, envvar='AWS_ACCOUNT_ID', help='Your AWS account ID (default: $AWS_ACCOUNT_ID)')
@click.option('--project-type', type=click.Choice(['ruby-rack', 'ruby-rails', 'nodejs', 'elixir', 'python-wsgi']), required=True, help='The type of project')
@click.option('--project-name', type=click.STRING, default=os.path.basename(os.getcwd()), help='The project name (default: name of current directory)')
@click.option('--aws-ecr-region', type=click.STRING, default='us-east-1', envvar='AWS_DEFAULT_REGION', help='Your AWS ECR region (default: $AWS_DEFAULT_REGION or \'us-east-1\')')
@click.option('--port', type=click.INT, default=80, help='The port of the service (default: 80)')
@click.option('--internal', type=click.BOOL, is_flag=True, help='Create an internal Kubernetes service definition')
def setup(aws_account_id, project_type, project_name, aws_ecr_region, port, internal):
  """Set up Hokusai for the current project"""
  hokusai.setup(aws_account_id, project_type, project_name, aws_ecr_region, port, internal)


@base.command(context_settings=CONTEXT_SETTINGS)
def check():
  """Check Hokusai dependencies and configuration"""
  hokusai.check()


@base.command(context_settings=CONTEXT_SETTINGS)
def version():
  """Print Hokusai's version and exit"""
  hokusai.version()
