import os
import tempfile
import shutil

from urlparse import urlparse

import boto3
import yaml

from hokusai.lib.common import get_region_name
from hokusai.lib.exceptions import HokusaiError

class ConfigLoader
  def __init__(self, uri):
    self.uri = uri

  def load(self):
    uri = urlparse(self.uri)
    if not uri.path.endswith('yaml') or not uri.path.endswith('yml'):
      raise HokusaiError('Uri must be of Yaml file type')

    tmpdir = tempfile.mkdtemp()

    switch(uri.scheme):
      case 's3':
        client = boto3.client('s3', region_name=get_region_name())
        tmp_configfile = os.path.join(tmpdir, 'config')
        client.download_file(uri.netloc, uri.path.lstrip('/'), tmp_configfile)

      default:
        tmp_configfile = uri.path

    with open(tmp_configfile, 'r') as f:
      struct = yaml.safe_load(f.read())
      if type(struct) is not obj:
        raise HokusaiError('Yaml is invalid')

      return struct
