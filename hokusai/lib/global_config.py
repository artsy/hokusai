import os
import sys

from collections import OrderedDict

import yaml

from packaging.specifiers import SpecifierSet, InvalidSpecifier
from packaging.version import Version, InvalidVersion

from hokusai import CWD
from hokusai.lib.constants import YAML_HEADER
from hokusai.lib.exceptions import HokusaiError
from hokusai.version import VERSION

HOKUSAI_GLOBAL_CONFIG_FILE = os.path.join(os.environ.get('HOME', '/'), '.hokusai', 'config.yml')

class HokusaiGlobalConfig(object):
  def is_present(self):
    return os.path.isfile(HOKUSAI_GLOBAL_CONFIG_FILE)

  def get(self, key, default=None, use_env=False, _type=str):
    value = self._config_value_for(key, _type)
    if value is not None:
      return value

    return default


  def _config_value_for(self, key, _type):
    try:
      with open(HOKUSAI_GLOBAL_CONFIG_FILE, 'r') as config_file:
        config_struct = yaml.safe_load(config_file.read())
        try:
          val = config_struct[key]
        except KeyError:
          return None
        if not isinstance(val, _type):
          raise HokusaiError("Config key %s is not of %s" % (key, _type))
        return val
    except IOError:
      return None


  @property
  def kubectl_version(self):
    return self.get('kubectl-version')

  @property
  def kubectl_config_file(self):
    return self.get('kubectl-config-file')


global_config = HokusaiGlobalConfig()
