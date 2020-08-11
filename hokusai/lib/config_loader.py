import os
import sys
import tempfile
from shutil import rmtree, copyfile

if sys.version_info[0] >= 3:
  from urllib.parse import urlparse
else:
  from urlparse import urlparse

import boto3
import yaml

from botocore.exceptions import ClientError

from hokusai.lib.common import get_region_name
from hokusai.lib.exceptions import HokusaiError

class ConfigLoader:
  def __init__(self, uri):
    self.uri = uri

  def load(self):
    uri = urlparse(self.uri)
    if not uri.path.endswith('yaml') and not uri.path.endswith('yml'):
      raise HokusaiError('Uri must be of Yaml file type')

    tmpdir = tempfile.mkdtemp()
    tmp_configfile = os.path.join(tmpdir, 'config')

    try:
      if uri.scheme == 's3':
        client = boto3.client('s3', region_name=get_region_name())
        try:
          client.download_file(uri.netloc, uri.path.lstrip('/'), tmp_configfile)
        except ClientError:
          raise HokusaiError("Error fetching file %s" % self.uri)
      else:
        try:
          copyfile(uri.path, tmp_configfile)
        except IOError:
          raise HokusaiError("Error copying file %s" % self.uri)

      with open(tmp_configfile, 'r') as f:
        struct = yaml.safe_load(f.read())
        if type(struct) is not dict:
          raise HokusaiError('Yaml is invalid')
        return struct

    except HokusaiError:
      raise

    finally:
      rmtree(tmpdir)
