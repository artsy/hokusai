import os
import shutil
import tempfile

from distutils.dir_util import mkpath
from urllib.request import urlretrieve

from hokusai.lib.command import command
from hokusai.lib.common import print_green, get_platform, uri_to_local
from hokusai.lib.global_config import HokusaiGlobalConfig


def install_kubectl(kubectl_version, kubectl_dir):
  ''' download and install kubectl '''
  tmpdir = tempfile.mkdtemp()
  url = (
    f"https://storage.googleapis.com/kubernetes-release/release/v" +
    f"{kubectl_version}" +
    f"/bin/{get_platform()}/amd64/kubectl"
  )
  print_green(f'Downloading kubectl from {url} ...', newline_after=True)
  urlretrieve(url, os.path.join(tmpdir, 'kubectl'))
  os.chmod(os.path.join(tmpdir, 'kubectl'), 0o755)
  print_green(f'Installing kubectl into {kubectl_dir} ...', newline_after=True)
  shutil.move(
    os.path.join(tmpdir, 'kubectl'),
    os.path.join(kubectl_dir, 'kubectl')
  )
  shutil.rmtree(tmpdir)

def install_kubeconfig(kubeconfig_source_uri, kubeconfig_dir):
  ''' download and install kubeconfig, name the file "config" in the given dir '''
  if not os.path.isdir(kubeconfig_dir):
    mkpath(kubeconfig_dir)
  print_green(f'Downloading kubeconfig from {kubeconfig_source_uri} to {kubeconfig_dir} ...', newline_after=True)
  uri_to_local(kubeconfig_source_uri, os.path.join(kubeconfig_dir, 'config'))

def install(global_config, skip_kubeconfig, skip_kubectl):
  ''' install kubeconfig and kubectl '''
  if not skip_kubeconfig:
    install_kubeconfig(
      global_config.kubeconfig_source_uri,
      global_config.kubeconfig_dir
    )
  if not skip_kubectl:
    install_kubectl(
      global_config.kubectl_version,
      global_config.kubectl_dir
    )

@command(config_check=False)
def configure(kubeconfig_dir, kubectl_dir, new_config, skip_kubeconfig, skip_kubectl):
  '''
  read new global config,
  save global config,
  install kubeconfig and kubectl
  '''
  global_config = HokusaiGlobalConfig(config_path=new_config)
  # override global config with cmdline options
  global_config.merge(
    kubectl_dir=kubectl_dir,
    kubeconfig_dir=kubeconfig_dir,
  )
  global_config.save()
  install(global_config, skip_kubeconfig, skip_kubectl)
