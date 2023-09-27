import os
import shutil
import tempfile

from urllib.request import urlretrieve

from hokusai.lib.command import command
from hokusai.lib.common import print_green, print_red, get_platform, local_to_local, uri_to_local
from hokusai.lib.global_config import HokusaiGlobalConfig


def install_kubectl(kubectl_version, kubectl_dir):
  ''' download and install kubectl '''
  tmpdir = tempfile.mkdtemp()
  try:
    url = (
      f"https://storage.googleapis.com/kubernetes-release/release/v" +
      f"{kubectl_version}" +
      f"/bin/{get_platform()}/amd64/kubectl"
    )
    download_to = os.path.join(tmpdir, 'kubectl')
    print_green(f'Downloading kubectl from {url} ...', newline_after=True)
    urlretrieve(url, download_to)
    print_green(f'Installing kubectl into {kubectl_dir} ...', newline_after=True)
    local_to_local(download_to, kubectl_dir, 'kubectl', mode=0o770)
  except:
    print_red(f'Error: Failed to install kubectl')
    raise
  finally:
    shutil.rmtree(tmpdir)

def install(global_config, skip_kubeconfig, skip_kubectl):
  ''' install kubeconfig and kubectl '''
  if not skip_kubeconfig:
    print_green(
      f'Downloading kubeconfig from ' +
      f'{global_config.kubeconfig_source_uri} ' +
      f'to {global_config.kubeconfig_dir} ...',
      newline_after=True
    )
    uri_to_local(
      global_config.kubeconfig_source_uri,
      global_config.kubeconfig_dir,
      'config'
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
  if new_config:
    global_config = HokusaiGlobalConfig(uri=new_config)
  else:
    global_config = HokusaiGlobalConfig()
  # override global config with cmdline options
  global_config.merge(
    kubectl_dir=kubectl_dir,
    kubeconfig_dir=kubeconfig_dir,
  )
  global_config.save()
  install(global_config, skip_kubeconfig, skip_kubectl)
