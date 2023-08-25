import os
import yaml

from hokusai.lib.common import print_red
from hokusai.lib.exceptions import HokusaiError

HOKUSAI_GLOBAL_CONFIG_FILE = os.path.join(os.environ.get('HOME', '/'), '.hokusai', 'config.yml')

class HokusaiGlobalConfig:
  def __init__(self):
    self.config = {}
    try:
      with open(HOKUSAI_GLOBAL_CONFIG_FILE, 'r') as config_file:
        self.config = yaml.safe_load(config_file.read())
    except:
      print_red(f'Error: Not able to read global configuration file {HOKUSAI_GLOBAL_CONFIG_FILE}')
      raise

global_config = HokusaiGlobalConfig()
