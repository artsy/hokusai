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

from hokusai.services.s3 import s3_interface

class ConfigLoader:
  def __init__(self, uri):
    self.uri = uri

  def load_from_s3(self, bucket_name, key_name, tmp_configfile):
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
    parsed_uri = urlparse(self.uri)
    if not parsed_uri.path.endswith('yaml') and not parsed_uri.path.endswith('yml'):
      raise HokusaiError('Uri must be of Yaml file type')

    tmpdir = tempfile.mkdtemp()
    tmp_configfile = os.path.join(tmpdir, 'hokusai_config.yml')

    try:
      if parsed_uri.scheme == 's3':
        bucket_name = parsed_uri.netloc
        key_name = parsed_uri.path.lstrip('/')
        s3_interface.download(bucket_name, key_name, tmp_configfile)
        config = self.load_from_file(tmp_configfile)
      elif parsed_uri.scheme == 'file':
        config = self.load_from_file(parsed_uri.path)
      else:
        raise HokusaiError("Hokusai config file path must have a scheme of 'file:///' or 's3://'")
      return config
    except:
      print_red(f'Error: Not able to load config from {self.uri}')
      raise
    finally:
      rmtree(tmpdir)
