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
def configure(install_to, install_config_to, platform, s3_location_of_org_hokusai_config):
  org_hokusai_config = parse_org_hokusai_config(s3_location_of_org_hokusai_config)
  validate_org_config(org_hokusai_config)
  user_hokusai_config = create_user_hokusai_config(org_hokusai_config, install_to, install_config_to, platform)
  install_kubectl(user_hokusai_config)
  install_kubeconfig(user_hokusai_config)
  save_user_hokusai_config(user_hokusai_config)

def create_user_hokusai_config(org_hokusai_config, install_to, install_config_to, platform):
  user_hokusai_config = org_hokusai_config
  if install_to:
    user_hokusai_config['install_to'] = install_to
  if install_config_to:
    user_hokusai_config['install_config_to'] = install_config_to
  if platform:
    user_hokusai_config['platform'] = platform
  return user_hokusai_config

def validate_org_config(org_hokusai_config):
  # required vars
  required_vars = [
    'kubectl_version',
    's3_bucket',
    's3_key'
  ]
  for var in required_vars:
    if not org_hokusai_config[var]:
      print_red(f'Error: {var} is not set in org Hokusai config')

def install_kubectl(user_hokusai_config):
  print_green("Downloading and installing kubectl...", newline_before=True, newline_after=True)
  tmpdir = tempfile.mkdtemp()
  urlretrieve("https://storage.googleapis.com/kubernetes-release/release/v%s/bin/%s/amd64/kubectl" % (kubectl_version, platform.system().lower()), os.path.join(tmpdir, 'kubectl'))
  os.chmod(os.path.join(tmpdir, 'kubectl'), 0o755)
  shutil.move(os.path.join(tmpdir, 'kubectl'), os.path.join(install_to, 'kubectl'))
  shutil.rmtree(tmpdir)

def install_kubeconfig(user_hokusai_config):
  print_green("Configuring kubectl...", newline_after=True)
  if not os.path.isdir(install_config_to):
    mkpath(install_config_to)

  if bucket_name and key_name:
    client = boto3.client('s3', region_name=get_region_name())
    client.download_file(bucket_name, key_name.lstrip('/'), os.path.join(install_config_to, 'config'))
  else:
    shutil.copy(config_file, os.path.join(install_config_to, 'config'))

  write_config_file(install_to)

def save_user_hokusai_config(user_hokusai_config):
  HOKUSAI_CONFIG_FILE = os.path.join(os.environ.get('HOME'), '.hokusai.conf')
  try:
    with open(HOKUSAI_CONFIG_FILE, 'w') as output:
      output.write(YAML_HEADER)
      yaml.safe_dump(user_hokusai_config, output, default_flow_style=False)
  except:
    print_red(f'Error: Not able to write user Hokusai configuration file {HOKUSAI_CONFIG_FILE}')
    raise
