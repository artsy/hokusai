import os
import tempfile
import yaml

from shutil import rmtree

from hokusai.lib.common import print_red, uri_to_local
from hokusai.lib.exceptions import HokusaiError


class ConfigLoader:
  ''' load Hokusai config from Yaml files '''
  def __init__(self, uri):
    self.uri = uri

  def _load_from_file(self, file_path):
    ''' load config from file '''
    with open(file_path, 'r') as f:
      struct = yaml.safe_load(f.read())
      return struct

  def load(self):
    ''' load config from uri '''
    if not self.uri.endswith('yaml') and not self.uri.endswith('yml'):
      raise HokusaiError('Config file must be of Yaml file type')

    tmpdir = tempfile.mkdtemp()
    filename = 'hokusai.yml'
    tmp_configfile = os.path.join(tmpdir, filename)

    try:
      uri_to_local(self.uri, tmpdir, filename)
      config = self._load_from_file(tmp_configfile)
      return config
    except:
      print_red(f'Error: Not able to load config from {self.uri}')
      raise
    finally:
      rmtree(tmpdir)
