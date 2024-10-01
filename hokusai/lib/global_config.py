import os
import yaml

from hokusai.lib.common import (
  local_to_local,
  print_red,
  unlink_file_if_not_debug,
  write_temp_file,
  yaml_content_with_header
)
from hokusai.lib.config import HOKUSAI_TMP_DIR
from hokusai.lib.config_loader import ConfigLoader
from hokusai.lib.exceptions import HokusaiError


user_home = os.environ.get('HOME', '/')
local_global_config_file_name = '.hokusai.yml'
local_global_config = os.path.join(
  user_home,
  local_global_config_file_name
)
source_global_config = os.environ.get(
  'HOKUSAI_GLOBAL_CONFIG',
  local_global_config
)

class HokusaiGlobalConfig:
  ''' manage Hokusai global config '''
  def __init__(self):
    self._config = ConfigLoader(source_global_config).load()
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
      config_string = yaml.safe_dump(
        self._config,
        default_flow_style=False
      )
      tmp_path = write_temp_file(
        yaml_content_with_header(config_string),
        HOKUSAI_TMP_DIR
      )
      local_to_local(
        tmp_path,
        user_home,
        local_global_config_file_name,
        create_target_dir=False
      )
      unlink_file_if_not_debug(tmp_path)
    except:
      print_red(
        f'Error: Not able to write Hokusai config to {local_global_config}'
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
