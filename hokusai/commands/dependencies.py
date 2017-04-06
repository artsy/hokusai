import os
import urllib
import shutil

from distutils.dir_util import mkpath

import boto3

from hokusai.command import command
from hokusai.common import print_red, print_green

@command
def dependencies(kubectl_version, platform, install_to, install_kubeconfig_to, bucket_name, key_name, bucket_region):
  print_green("Downloading and installing kubectl...")
  urllib.urlretrieve("https://storage.googleapis.com/kubernetes-release/release/v%s/bin/%s/amd64/kubectl" % (kubectl_version, platform), os.path.join('/tmp', 'kubectl'))
  os.chmod(os.path.join('/tmp', 'kubectl'), 0755)
  shutil.move(os.path.join('/tmp', 'kubectl'), os.path.join(install_to, 'kubectl'))

  print_green("Configuring kubectl...")
  if not os.path.isdir(install_kubeconfig_to):
    mkpath(install_kubeconfig_to)

  bucket = boto3.resource('s3').Bucket(bucket_name)
  bucket.download_file(key_name, os.path.join(install_kubeconfig_to, 'config'))
