import os
import urllib
import shutil

from distutils.dir_util import mkpath

import boto
from boto.s3.key import Key

from hokusai.common import print_red, print_green

def install(kubectl_version, platform, install_to, install_kubeconfig_to, bucket_name, key_name, bucket_region):
  try:
    print_green("Downloading and installing kubectl...")
    urllib.urlretrieve("https://storage.googleapis.com/kubernetes-release/release/v%s/bin/%s/amd64/kubectl" % (kubectl_version, platform), os.path.join('/tmp', 'kubectl'))
    os.chmod(os.path.join('/tmp', 'kubectl'), 0755)
    shutil.move(os.path.join('/tmp', 'kubectl'), os.path.join(install_to, 'kubectl'))
  except Exception, e:
    print_red("Error installing kubectl: %s" % repr(e))
    return -1

  try:
    print_green("Configuring kubectl...")
    if not os.path.isdir(install_kubeconfig_to):
      mkpath(install_kubeconfig_to)

    conn = boto.s3.connect_to_region(bucket_region)
    bucket = conn.get_bucket(conn.lookup(bucket_name))
    k = Key(bucket)
    k.key = key_name
    k.get_contents_to_filename(os.path.join(install_kubeconfig_to, 'config'))

  except Exception, e:
    print_red("Error configuring kubectl: %s" % repr(e))
    return -1

  return 0
