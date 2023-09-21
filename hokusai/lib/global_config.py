import os
import sys

from collections import OrderedDict

import yaml

from packaging.specifiers import SpecifierSet, InvalidSpecifier
from packaging.version import Version, InvalidVersion

from hokusai import CWD
from hokusai.lib.common import print_red
from hokusai.lib.constants import YAML_HEADER
from hokusai.lib.exceptions import HokusaiError
from hokusai.version import VERSION

from hokusai.lib.config_loader import ConfigLoader

HOKUSAI_GLOBAL_CONFIG_FILE = os.path.join(os.environ.get('HOME', '/'), '.hokusai_config.yml')

class HokusaiGlobalConfig:
  def __init__(self):
    # load config from default config file
    self.load_config(f'file://{HOKUSAI_GLOBAL_CONFIG_FILE}')

  def load_config(self, config_path):
    ''' load config from specified path '''
    config = ConfigLoader(config_path).load()
    self.validate_config(config)
    self.config = config

  def merge(self, **kwargs):
    ''' merge params into config '''
    for k,v in kwargs.items():
      if v is not None:
        self.config[k] = v

  def validate_config(self, config):
    ''' sanity check config '''
    required_vars = [
      'kubectl_version',
      'kubeconfig_s3_bucket',
      'kubeconfig_s3_key'
    ]
    for var in required_vars:
      if not config[var]:
        print_red(f'Error: {var} is missing in Hokusai config')

  def save(self):
    ''' save config to ~/.hokusai.conf '''
    try:
      with open(HOKUSAI_GLOBAL_CONFIG_FILE, 'w') as output:
        output.write(YAML_HEADER)
        yaml.safe_dump(self.config, output, default_flow_style=False)
    except:
      print_red(f'Error: Not able to write Hokusai config to {file_path}')
      raise

  @property
  def kubectl_version(self):
    return self.config['kubectl_version']

  @property
  def kubectl_dir(self):
    return self.config['kubectl_dir']

  @property
  def kubeconfig_s3_bucket(self):
    return self.config['kubeconfig_s3_bucket']

  @property
  def kubeconfig_s3_key(self):
    return self.config['kubeconfig_s3_key']

  @property
  def kubeconfig_dir(self):
    return self.config['kubeconfig_dir']

global_config = HokusaiGlobalConfig()
