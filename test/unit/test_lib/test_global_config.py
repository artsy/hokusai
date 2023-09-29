import os
import pytest
import tempfile
import yaml

import hokusai.lib.global_config

from hokusai.lib.exceptions import HokusaiError
from hokusai.lib.global_config import HokusaiGlobalConfig


def describe_hokusai_global_config():
  def describe_init():
    def it_inits():
      config_file = os.path.join(os.environ['HOME'], '.hokusai.yml')
      config_obj = HokusaiGlobalConfig(config_file)
      assert config_obj._config['kubeconfig-dir'] == '/tmp/.kube'

  def describe_merge():
    def it_merges():
      config_file = os.path.join(os.environ['HOME'], '.hokusai.yml')
      config_obj = HokusaiGlobalConfig(config_file)
      config_obj.merge(
        kubeconfig_dir='foodir',
        kubeconfig_source_uri=None
      )
      assert config_obj._config['kubeconfig-dir'] == 'foodir'
      assert config_obj._config['kubeconfig-source-uri'] == '/fake/path/to/kube/config'

  def describe_save():
    def it_saves(monkeypatch):
      config_file = os.path.join(os.environ['HOME'], '.hokusai.yml')
      config_obj = HokusaiGlobalConfig(config_file)
      config_obj.merge(kubeconfig_dir='foodir')
      with tempfile.TemporaryDirectory() as tmpdir:
        file_path = os.path.join(tmpdir, '.hokusai.yml')
        monkeypatch.setattr(hokusai.lib.global_config, "HOKUSAI_GLOBAL_CONFIG_FILE", file_path)
        config_obj.save()
        with open(file_path, 'r') as f:
          struct = yaml.safe_load(f.read())
          assert struct['kubeconfig-dir'] == 'foodir'

  def describe_validate_config():
    def it_raises_when_required_var_missing():
      config_file = os.path.join(os.environ['HOME'], '.hokusai.yml')
      config_obj = HokusaiGlobalConfig(config_file)
      del config_obj._config['kubeconfig-dir']
      with pytest.raises(HokusaiError):
        config_obj.validate_config()
    def it_does_not_raise_when_otherwise():
      config_file = os.path.join(os.environ['HOME'], '.hokusai.yml')
      config_obj = HokusaiGlobalConfig(config_file)
      config_obj.validate_config()

  def describe_kubeconfig_dir():
    def it_returns_the_correct_var():
      config_file = os.path.join(os.environ['HOME'], '.hokusai.yml')
      config_obj = HokusaiGlobalConfig(config_file)
      assert config_obj.kubeconfig_dir == config_obj._config['kubeconfig-dir']
