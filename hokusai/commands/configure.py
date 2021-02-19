import os
import platform
import urllib
import shutil
import tempfile
import sys

from distutils.dir_util import mkpath

if sys.version_info[0] >= 3:
  from urllib.parse import urlparse
  from urllib.request import urlretrieve
else:
  from urlparse import urlparse
  from urllib import urlretrieve

import boto3

from hokusai.lib.global_config import global_config
from hokusai.lib.command import command
from hokusai.lib.common import print_green, get_region_name
from hokusai.lib.exceptions import HokusaiError

@command(config_check=False)
def configure(kubectl_version, bucket_name, key_name, config_file, install_to, install_config_to):
  if global_config.is_present() and global_config.kubectl_version is not None:
    kubectl_version = global_config.kubectl_version

  if not kubectl_version:
    raise HokusaiError("You must supply a kubectl_version")

  if global_config.is_present() and global_config.kubectl_config_file is not None:
    uri = urlparse(global_config.kubectl_config_file)
    if uri.scheme == 's3':
      bucket_name = uri.netloc
      key_name = uri.path
    if uri.scheme == 'file':
      key_name = uri.path

  if not ((bucket_name and key_name) or config_file):
    raise HokusaiError("You must define valid config_file")

  print_green("Downloading and installing kubectl...", newline_before=True, newline_after=True)
  tmpdir = tempfile.mkdtemp()
  urlretrieve("https://storage.googleapis.com/kubernetes-release/release/v%s/bin/%s/amd64/kubectl" % (kubectl_version, platform.system().lower()), os.path.join(tmpdir, 'kubectl'))
  os.chmod(os.path.join(tmpdir, 'kubectl'), 0o755)
  shutil.move(os.path.join(tmpdir, 'kubectl'), os.path.join(install_to, 'kubectl'))
  shutil.rmtree(tmpdir)

  print_green("Configuring kubectl...", newline_after=True)
  if not os.path.isdir(install_config_to):
    mkpath(install_config_to)

  if bucket_name and key_name:
    client = boto3.client('s3', region_name=get_region_name())
    client.download_file(bucket_name, key_name.lstrip('/'), os.path.join(install_config_to, 'config'))
  else:
    shutil.copy(config_file, os.path.join(install_config_to, 'config'))
