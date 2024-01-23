import os
import pytest
import yaml

import hokusai.lib.global_config
import test.unit.test_lib.fixtures.global_config

from hokusai.lib.exceptions import HokusaiError
from hokusai.lib.global_config import HokusaiGlobalConfig
from test.unit.test_lib.fixtures.global_config import mock_config_loader_class


def describe_hokusai_global_config():
  def describe_init():
    def describe_env_lacks_hokusai_global_config_var():
      def it_reads_local_config_file():
        config_obj = HokusaiGlobalConfig()
        assert config_obj._config['kubeconfig-dir'] == '/tmp/.kube'
    def describe_env_has_hokusai_global_config_var():
      def it_reads_file_specified_by_env_var(mocker, mock_config_loader_class, monkeypatch):
        mocker.patch('hokusai.lib.global_config.ConfigLoader').side_effect = mock_config_loader_class
        load_spy = mocker.spy(test.unit.test_lib.fixtures.global_config, 'load_for_spy')
        monkeypatch.setattr(hokusai.lib.global_config, "source_global_config", '/foo/path/to/hokusai.yml')
        # ^^ this patch is not exact. it patches module var, not env.
        # to patch env:
        # monkeypatch.setenv('HOKUSAI_GLOBAL_CONFIG', '/foo/path/to/hokusai.yml')
        # but it doesn't work. it's too late,
        # global_config.py has already been loaded,
        # os.environ.get has already been run, and won't be run again.
        obj = HokusaiGlobalConfig()
        load_spy.assert_has_calls([
          mocker.call(
            '/foo/path/to/hokusai.yml'
          )
        ])

  def describe_merge():
    def it_merges():
      config_file = os.path.join(os.environ['HOME'], '.hokusai.yml')
      config_obj = HokusaiGlobalConfig()
      config_obj.merge(
        kubeconfig_dir='foodir',
        kubeconfig_source_uri=None
      )
      assert config_obj._config['kubeconfig-dir'] == 'foodir'
      assert config_obj._config['kubeconfig-source-uri'] == '/fake/path/to/kube/config'

  def describe_save():
    def it_saves(monkeypatch, tmp_path):
      config_file = os.path.join(os.environ['HOME'], '.hokusai.yml')
      config_obj = HokusaiGlobalConfig()
      config_obj.merge(kubeconfig_dir='foodir')
      file_path = os.path.join(tmp_path, '.hokusai.yml')
      monkeypatch.setattr(hokusai.lib.global_config, "local_global_config", file_path)
      config_obj.save()
      with open(file_path, 'r') as f:
        struct = yaml.safe_load(f.read())
        assert struct['kubeconfig-dir'] == 'foodir'

  def describe_validate_config():
    def it_raises_when_required_var_missing():
      config_file = os.path.join(os.environ['HOME'], '.hokusai.yml')
      config_obj = HokusaiGlobalConfig()
      del config_obj._config['kubeconfig-dir']
      with pytest.raises(HokusaiError):
        config_obj.validate_config()
    def it_does_not_raise_when_otherwise():
      config_file = os.path.join(os.environ['HOME'], '.hokusai.yml')
      config_obj = HokusaiGlobalConfig()
      config_obj.validate_config()

  def describe_kubeconfig_dir():
    def it_returns_the_correct_var():
      config_file = os.path.join(os.environ['HOME'], '.hokusai.yml')
      config_obj = HokusaiGlobalConfig()
      assert config_obj.kubeconfig_dir == config_obj._config['kubeconfig-dir']
