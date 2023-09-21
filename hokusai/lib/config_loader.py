import os
import sys
import tempfile
from shutil import rmtree, copyfile
from urllib.parse import urlparse

import boto3
import yaml

from botocore.exceptions import ClientError

from hokusai.lib.common import get_region_name
from hokusai.lib.exceptions import HokusaiError

from hokusai.lib.common import print_red, s3_path, verbose_print_green

from hokusai.lib.common import print_red, get_verbosity

class ConfigLoader:
  def __init__(self, uri):
    self.uri = uri

  def load_from_s3(self, uri, tmp_configfile):
    verbose_print_green(f'Downloading {uri} to {tmp_configfile} ...', newline_after=True)
    client = boto3.client('s3', region_name=get_region_name())
    bucket_name = uri.netloc
    key_name = uri.path.lstrip('/')
    client.download_file(uri.netloc, uri.path.lstrip('/'), tmp_configfile)
    return self.load_from_file(tmp_configfile)

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
    uri = urlparse(self.uri)
    if not uri.path.endswith('yaml') and not uri.path.endswith('yml'):
      raise HokusaiError('Uri must be of Yaml file type')

    tmpdir = tempfile.mkdtemp()
    tmp_configfile = os.path.join(tmpdir, 'hokusai_config.yml')

    try:
      if uri.scheme == 's3':
        config = self.load_from_s3(uri, tmp_configfile)
      elif uri.scheme == 'file':
        config = self.load_from_file(uri.path)
      else:
        raise HokusaiError("Hokusai config file path must have a scheme of 'file:///' or 's3://'")
      return config
    except:
      print_red(f'Error: Not able to load config from {self.uri}')
      raise
    finally:
      rmtree(tmpdir)
