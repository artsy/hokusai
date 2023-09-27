import os
import yaml

from hokusai.lib.common import print_red
from hokusai.lib.config_loader import ConfigLoader
from hokusai.lib.constants import YAML_HEADER
from hokusai.lib.exceptions import HokusaiError


HOKUSAI_GLOBAL_CONFIG_FILE = os.path.join(os.environ.get('HOME', '/'), '.hokusai.yml')

class HokusaiGlobalConfig:
  ''' manage Hokusai global config '''
  def __init__(self, uri=HOKUSAI_GLOBAL_CONFIG_FILE):
    self._config = ConfigLoader(uri).load()
    self.validate_config()

  def merge(self, **kwargs):
    ''' merge key/value pairs into config, skipping None '''
    for k,v in kwargs.items():
      if v is not None:
        # use dash in _config keys
        self._config[k.replace('_', '-')] = v

  def save(self):
    ''' save config to local config file '''
    try:
      with open(HOKUSAI_GLOBAL_CONFIG_FILE, 'w') as output:
        output.write(YAML_HEADER)
        yaml.safe_dump(
          self._config,
          output,
          default_flow_style=False
        )
    except:
      print_red(
        f'Error: Not able to write Hokusai config to {file_path}'
      )
      raise

  def validate_config(self):
    ''' sanity check config '''
    required_vars = [
      'kubectl-version',
      'kubeconfig-dir',
      'kubeconfig-source-uri',
      'kubectl-dir'
    ]
    for var in required_vars:
      if not var in self._config:
        raise HokusaiError(
          f'{var} is missing in Hokusai global config'
        )

  @property
  def kubeconfig_dir(self):
    return self._config['kubeconfig-dir']

  @property
  def kubeconfig_source_uri(self):
    return self._config['kubeconfig-source-uri']

  @property
  def kubectl_dir(self):
    return self._config['kubectl-dir']

  @property
  def kubectl_version(self):
    return self._config['kubectl-version']
