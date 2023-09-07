import os
import platform
import shutil
import tempfile
import sys
from urllib.parse import urlparse
from urllib.request import urlretrieve

from distutils.dir_util import mkpath

import boto3

from hokusai.lib.command import command
from hokusai.lib.common import print_green, get_region_name
from hokusai.lib.exceptions import HokusaiError

from hokusai.lib.constants import YAML_HEADER
from hokusai.lib.common import print_red
import yaml


@command(config_check=False)
def configure(install_to, install_config_to, platform, s3_location_of_org_config):
  org_config = parse_org_config(s3_location_of_org_config)
  validate_org_config(org_config)

  user_config = create_user_config(org_config, install_to, install_config_to, platform)

  install_kubectl(
    user_config['kubectl_version'],
    user_config['platform'],
    user_config['install_to']
  )

  install_kubeconfig(
    user_config['install_config_to'],
    user_config['bucket_name'],
    user_config['key_name']
  )

  save_user_config(user_config)

def create_user_config(org_config, install_to, install_config_to, platform):
  user_config = org_config
  user_config['install_to'] = install_to
  user_config['install_config_to'] = install_config_to
  user_config['platform'] = platform
  return user_config

def install_kubeconfig(install_config_to, bucket_name, key_name):
  print_green("Setting up kubeconfig file...", newline_after=True)
  if not os.path.isdir(install_config_to):
    mkpath(install_config_to)
  client = boto3.client('s3', region_name=get_region_name())
  client.download_file(bucket_name, key_name.lstrip('/'), os.path.join(install_config_to, 'config'))

def install_kubectl(kubectl_version, platform, install_to):
  print_green("Downloading and installing kubectl...", newline_before=True, newline_after=True)
  tmpdir = tempfile.mkdtemp()
  urlretrieve(
    f"https://storage.googleapis.com/kubernetes-release/release/v" +
    f"{kubectl_version}" +
    f"/bin/{platform.system().lower()}/amd64/kubectl" +
    os.path.join(tmpdir, 'kubectl')
  )
  os.chmod(os.path.join(tmpdir, 'kubectl'), 0o755)
  shutil.move(
    os.path.join(tmpdir, 'kubectl'),
    os.path.join(install_to, 'kubectl')
  )
  shutil.rmtree(tmpdir)

def save_user_config(user_config):
  CONFIG_FILE = os.path.join(os.environ.get('HOME'), '.hokusai.conf')
  try:
    with open(CONFIG_FILE, 'w') as output:
      output.write(YAML_HEADER)
      yaml.safe_dump(user_config, output, default_flow_style=False)
  except:
    print_red(f'Error: Not able to write user Hokusai configuration file {CONFIG_FILE}')
    raise

def validate_org_config(org_config):
  required_vars = [
    'kubectl_version',
    's3_bucket',
    's3_key'
  ]
  for var in required_vars:
    if not org_config[var]:
      print_red(f'Error: {var} must be set in org Hokusai config')
