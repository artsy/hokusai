import os
import pytest
import tempfile

import hokusai.commands.configure

from hokusai.commands.configure import hokusai_configure, install, install_kubectl
from hokusai.lib.common import get_platform
from test.unit.test_commands.fixtures.configure import mock_global_config, mock_urlretrieve_raise


def describe_install():
  def describe_no_skip():
    def it_calls_properly(mocker, mock_global_config):
      mocker.patch('hokusai.commands.configure.uri_to_local')
      uri_to_local_spy = mocker.spy(hokusai.commands.configure, 'uri_to_local')
      mocker.patch('hokusai.commands.configure.install_kubectl')
      install_kubectl_spy = mocker.spy(hokusai.commands.configure, 'install_kubectl')
      global_config = mock_global_config()
      install(global_config, False, False)
      uri_to_local_spy.assert_has_calls([
        mocker.call(
          global_config.kubeconfig_source_uri,
          global_config.kubeconfig_dir,
          'config'
        )
      ])
      install_kubectl_spy.assert_has_calls([
        mocker.call(
          global_config.kubectl_version,
          global_config.kubectl_dir
        )
      ])
  def describe_skip_kubeconfig():
    def it_calls_properly(mocker, mock_global_config):
      mocker.patch('hokusai.commands.configure.uri_to_local')
      uri_to_local_spy = mocker.spy(hokusai.commands.configure, 'uri_to_local')
      mocker.patch('hokusai.commands.configure.install_kubectl')
      install_kubectl_spy = mocker.spy(hokusai.commands.configure, 'install_kubectl')
      global_config = mock_global_config()
      install(global_config, True, False)
      assert uri_to_local_spy.call_count == 0
      install_kubectl_spy.assert_has_calls([
        mocker.call(
          global_config.kubectl_version,
          global_config.kubectl_dir
        )
      ])
  def describe_skip_kubectl():
    def it_calls_properly(mocker, mock_global_config):
      mocker.patch('hokusai.commands.configure.uri_to_local')
      uri_to_local_spy = mocker.spy(hokusai.commands.configure, 'uri_to_local')
      mocker.patch('hokusai.commands.configure.install_kubectl')
      install_kubectl_spy = mocker.spy(hokusai.commands.configure, 'install_kubectl')
      global_config = mock_global_config()
      install(global_config, False, True)
      uri_to_local_spy.assert_has_calls([
        mocker.call(
          global_config.kubeconfig_source_uri,
          global_config.kubeconfig_dir,
          'config'
        )
      ])
      assert install_kubectl_spy.call_count == 0
  def describe_skip_both():
    def it_calls_properly(mocker, mock_global_config):
      mocker.patch('hokusai.commands.configure.uri_to_local')
      uri_to_local_spy = mocker.spy(hokusai.commands.configure, 'uri_to_local')
      mocker.patch('hokusai.commands.configure.install_kubectl')
      install_kubectl_spy = mocker.spy(hokusai.commands.configure, 'install_kubectl')
      global_config = mock_global_config()
      install(global_config, True, True)
      assert uri_to_local_spy.call_count == 0
      assert install_kubectl_spy.call_count == 0

def describe_install_kubectl():
  def it_calls_properly(mocker):
    mocker.patch('hokusai.commands.configure.urlretrieve')
    retrieve_spy = mocker.spy(hokusai.commands.configure, 'urlretrieve')
    mocker.patch('hokusai.commands.configure.local_to_local')
    local_to_local_spy = mocker.spy(hokusai.commands.configure, 'local_to_local')
    with tempfile.TemporaryDirectory() as tmpdir:
      mocker.patch('hokusai.commands.configure.tempfile.mkdtemp', return_value=tmpdir)
      install_kubectl('fooversion', 'foodir')
      url = f'https://storage.googleapis.com/kubernetes-release/release/vfooversion/bin/{get_platform()}/amd64/kubectl'
      download_to = os.path.join(tmpdir, 'kubectl')
      retrieve_spy.assert_has_calls([
        mocker.call(
          url,
          download_to
        )
      ])
      local_to_local_spy.assert_has_calls([
        mocker.call(
          download_to,
          'foodir',
          'kubectl',
          mode=0o770
        )
      ])
  def it_catches_exceptions(mocker, mock_urlretrieve_raise):
    mocker.patch('hokusai.commands.configure.urlretrieve').side_effect = mock_urlretrieve_raise
    with pytest.raises(Exception):
      install_kubectl('fooversion', 'foodir')
