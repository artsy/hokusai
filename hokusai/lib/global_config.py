import os
import yaml

from hokusai.lib.common import print_red

HOKUSAI_GLOBAL_CONFIG_FILE = os.path.join(os.environ.get('HOME', '/'), '.hokusai.conf')

def get_global_config():
  try:
    with open(HOKUSAI_GLOBAL_CONFIG_FILE, 'r') as config_file:
      config = yaml.safe_load(config_file.read())
  except:
    print_red(f'Error: Not able to read global configuration file {HOKUSAI_GLOBAL_CONFIG_FILE}')
    raise
  return config
