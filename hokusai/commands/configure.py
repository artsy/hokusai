import os
import platform
import shutil
import tempfile
import sys
from urllib.parse import urlparse
from urllib.request import urlretrieve

from distutils.dir_util import mkpath

import boto3

from hokusai.lib.command import command
from hokusai.lib.common import print_green, get_region_name
from hokusai.lib.exceptions import HokusaiError

from hokusai.lib.constants import YAML_HEADER
from hokusai.lib.common import print_red
import yaml


@command(config_check=False)
def configure(kubectl_version, bucket_name, key_name, config_file, install_to, install_config_to):
  if not kubectl_version:
    raise HokusaiError("You must supply a kubectl_version")

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

  write_config_file(install_to)

def write_config_file(install_to):
  HOKUSAI_GLOBAL_CONFIG_FILE = os.path.join(os.environ.get('HOME', '/'), '.hokusai', 'config.yml')
  obj = {'bin-dir': install_to}
  try:
    with open(HOKUSAI_GLOBAL_CONFIG_FILE, 'w') as output:
      output.write(YAML_HEADER)
      yaml.safe_dump(obj, output, default_flow_style=False)
  except:
    print_red(f'Error: Not able to write global configuration file {HOKUSAI_GLOBAL_CONFIG_FILE}')
    raise
