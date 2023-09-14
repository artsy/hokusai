import os
import platform
import shutil
import tempfile
import sys
import yaml

from distutils.dir_util import mkpath
from urllib.parse import urlparse
from urllib.request import urlretrieve

import boto3

from hokusai.lib.command import command
from hokusai.lib.common import print_green, print_red, get_region_name
from hokusai.lib.constants import YAML_HEADER
from hokusai.lib.exceptions import HokusaiError

def get_platform():
  return platform.system().lower()

def download_org_config_from_s3(bucket_name, key_name, file_path):
  client = boto3.client('s3', region_name=get_region_name())
  client.download_file(bucket_name, key_name.lstrip('/'), file_path)

def read_org_config_from_file(file_path):
  ''' read org config file '''
  try:
    with open(file_path, 'r') as org_config:
      org_config = yaml.safe_load(org_config.read())
  except:
    print_red(f'Error: Not able to read org-wide Hokusai config file')
    raise
  return org_config

def validate_org_config(org_config):
  required_vars = [
    'kubectl_version',
    'kubeconfig_s3_bucket',
    'kubeconfig_s3_key'
  ]
  for var in required_vars:
    if not org_config[var]:
      print_red(f'Error: {var} must be set in org-wide Hokusai config')

def read_org_config(org_config_path):
  uri = urlparse(org_config_path)
  if uri.scheme == 's3':
    bucket_name = uri.netloc
    key_name = uri.path
    with tempfile.TemporaryDirectory() as tmpdirname:
      file_path = os.path.join(tmpdirname, 'hokusai-org-config.yml')
      download_org_config_from_s3(bucket_name, key_name, file_path)
      org_config = read_org_config_from_file(file_path)
  elif uri.scheme == 'file':
    file_path = uri.path
    org_config = read_org_config_from_file(file_path)
  else:
    raise HokusaiError("The path to org-wide Hokusai config must have a scheme of 'file:///' or 's3://'")
  validate_org_config(org_config)
  return org_config

def create_user_config(org_config, kubectl_path, kubeconfig_path):
  user_config = org_config
  user_config['kubectl_path'] = kubectl_path
  user_config['kubeconfig_path'] = kubeconfig_path
  return user_config

def save_user_config(user_config):
  CONFIG_FILE = os.path.join(os.environ.get('HOME'), '.hokusai.conf')
  try:
    with open(CONFIG_FILE, 'w') as output:
      output.write(YAML_HEADER)
      yaml.safe_dump(user_config, output, default_flow_style=False)
  except:
    print_red(f'Error: Not able to write user Hokusai configuration file {CONFIG_FILE}')
    raise

def install_kubectl(kubectl_version, kubectl_path):
  print_green("Downloading and installing kubectl...", newline_before=True, newline_after=True)
  tmpdir = tempfile.mkdtemp()
  url = (
    f"https://storage.googleapis.com/kubernetes-release/release/v" +
    f"{kubectl_version}" +
    f"/bin/{get_platform()}/amd64/kubectl"
  )
  urlretrieve(url, os.path.join(tmpdir, 'kubectl'))
  os.chmod(os.path.join(tmpdir, 'kubectl'), 0o755)
  shutil.move(
    os.path.join(tmpdir, 'kubectl'),
    os.path.join(kubectl_path)
  )
  shutil.rmtree(tmpdir)

def install_kubeconfig(kubeconfig_path, bucket_name, key_name):
  print_green("Setting up kubeconfig file...", newline_after=True)
  if not os.path.isdir(kubeconfig_path):
    mkpath(kubeconfig_path)
  client = boto3.client('s3', region_name=get_region_name())
  client.download_file(bucket_name, key_name.lstrip('/'), kubeconfig_path)

@command(config_check=False)
def configure(org_config_path, kubectl_path, kubeconfig_path):
  org_config = read_org_config(org_config_path)

  user_config = create_user_config(
    org_config,
    kubectl_path,
    kubeconfig_path,
  )

  install_kubectl(
    user_config['kubectl_version'],
    user_config['kubectl_path']
  )

  install_kubeconfig(
    user_config['kubeconfig_path'],
    user_config['kubeconfig_s3_bucket'],
    user_config['k8s/config-dev']
  )

  save_user_config(user_config)
