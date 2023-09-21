import os
import tempfile
import yaml

from shutil import rmtree

from hokusai.lib.common import print_red, uri_to_local
from hokusai.lib.exceptions import HokusaiError


class ConfigLoader:
  def __init__(self, uri):
    self.uri = uri

  def load_from_file(self, file_path):
    with open(file_path, 'r') as f:
      struct = yaml.safe_load(f.read())
      return struct

  def load(self):
    '''
    load config from path
    path can be 'file:///path/to/file',
    or 's3://bucket/key
    '''
    if not self.uri.endswith('yaml') and not self.uri.endswith('yml'):
      raise HokusaiError('Config file must be of Yaml file type')

    tmpdir = tempfile.mkdtemp()
    tmp_configfile = os.path.join(tmpdir, 'hokusai_config.yml')

    try:
      uri_to_local(self.uri, tmp_configfile)
      config = self.load_from_file(tmp_configfile)
      return config
    except:
      print_red(f'Error: Not able to load config from {self.uri}')
      raise
    finally:
      rmtree(tmpdir)
