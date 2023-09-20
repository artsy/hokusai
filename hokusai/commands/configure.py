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
  ''' get the platform (e.g. darwin, linux) of the machine '''
  return platform.system().lower()

def download_from_s3(bucket_name, key_name, file_path):
  ''' download specified S3 file '''
  client = boto3.client('s3', region_name=get_region_name())
  client.download_file(bucket_name, key_name.lstrip('/'), file_path)

def read_config_from_file(file_path):
  ''' read Hokusai config from file '''
  try:
    with open(file_path, 'r') as config_file:
      config = yaml.safe_load(config_file.read())
  except:
    print_red(f'Error: Not able to read Hokusai config from {file_path}')
    raise
  return config

def validate_config(config):
  ''' sanity check Hokusai config '''
  required_vars = [
    'kubectl_version',
    'kubeconfig_s3_bucket',
    'kubeconfig_s3_key'
  ]
  for var in required_vars:
    if not config[var]:
      print_red(f'Error: {var} is missing in Hokusai config')

def read_config(config_path):
  ''' read Hokusai config from local file or S3 '''
  uri = urlparse(config_path)
  if uri.scheme == 's3':
    bucket_name = uri.netloc
    key_name = uri.path
    with tempfile.TemporaryDirectory() as tmpdirname:
      file_path = os.path.join(tmpdirname, 'hokusai.conf')
      download_from_s3(bucket_name, key_name, file_path)
      config = read_config_from_file(file_path)
  elif uri.scheme == 'file':
    file_path = uri.path
    config = read_config_from_file(file_path)
  else:
    raise HokusaiError("Hokusai config file path must have a scheme of 'file:///' or 's3://'")
  validate_config(config)
  return config

def create_final_config(config, kubectl_dir, kubeconfig_dir):
  ''' merge options into hokusai_config'''
  final_config = config
  if kubectl_dir is not None:
    final_config['kubectl_dir'] = kubectl_dir
  if kubeconfig_dir is not None:
    final_config['kubeconfig_dir'] = kubeconfig_dir
  return final_config

def save_config(config):
  ''' save Hokusai config to ~/.hokusai.conf '''
  file_path = os.path.join(os.environ.get('HOME'), '.hokusai.conf')
  try:
    with open(file_path, 'w') as output:
      output.write(YAML_HEADER)
      yaml.safe_dump(config, output, default_flow_style=False)
  except:
    print_red(f'Error: Not able to write Hokusai config to {file_path}')
    raise

def install_kubectl(kubectl_version, kubectl_dir):
  ''' download and install kubectl '''
  tmpdir = tempfile.mkdtemp()
  url = (
    f"https://storage.googleapis.com/kubernetes-release/release/v" +
    f"{kubectl_version}" +
    f"/bin/{get_platform()}/amd64/kubectl"
  )
  print_green(f'Downloading kubectl from {url} ...', newline_after=True)
  urlretrieve(url, os.path.join(tmpdir, 'kubectl'))
  os.chmod(os.path.join(tmpdir, 'kubectl'), 0o755)
  print_green(f'Installing kubectl into {kubectl_dir} ...', newline_after=True)
  shutil.move(
    os.path.join(tmpdir, 'kubectl'),
    os.path.join(kubectl_dir, 'kubectl')
  )
  shutil.rmtree(tmpdir)

def s3_path(bucket_name, key_name):
  ''' construct full s3 path s3://bucket_name/key '''
  return f"s3://{bucket_name}/{key_name.lstrip('/')}"

def install_kubeconfig(bucket_name, key_name, kubeconfig_dir):
  ''' download and install kubeconfig, name the file "config" in the given dir '''
  if not os.path.isdir(kubeconfig_dir):
    mkpath(kubeconfig_dir)
  client = boto3.client('s3', region_name=get_region_name())
  print_green(f'Downloading kubeconfig from {s3_path(bucket_name, key_name)} and installing it into {kubeconfig_dir} ...', newline_after=True)
  client.download_file(bucket_name, key_name.lstrip('/'), os.path.join(kubeconfig_dir, 'config'))

@command(config_check=False)
def configure(config_path, kubectl_dir, kubeconfig_dir):
  ''' configure Hokusai '''
  config = read_config(config_path)

  # options take precedence over config file
  final_config = create_final_config(
    config,
    kubectl_dir,
    kubeconfig_dir,
  )

  install_kubectl(
    final_config['kubectl_version'],
    final_config['kubectl_dir']
  )

  install_kubeconfig(
    final_config['kubeconfig_s3_bucket'],
    final_config['kubeconfig_s3_key'],
    final_config['kubeconfig_dir']
  )

  save_config(final_config)
