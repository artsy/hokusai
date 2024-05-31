import os
import pytest

import hokusai.lib.config_loader

from hokusai.lib.config_loader import ConfigLoader
from hokusai.lib.exceptions import HokusaiError
from test.unit.test_lib.fixtures.config_loader import mock_uri_to_local_raise


def describe_config_loader():
  def describe_init():
    def it_inits():
      loader = ConfigLoader('foouri')
      assert loader.uri == 'foouri'

  def describe_load_from_file():
    def it_loads():
      loader = ConfigLoader('foouri')
      config = loader._load_from_file('test/fixtures/template_config.yml')
      assert config['vars']['imageTag'] == 'eggs'

  def describe_load():
    def describe_yaml_type():
      def it_calls(mocker, tmp_path):
        mocker.patch('hokusai.lib.config_loader.uri_to_local')
        uri_to_local_spy = mocker.spy(hokusai.lib.config_loader, 'uri_to_local')
        loader = ConfigLoader('file:///test/fixtures/template_config.yml')
        mocker.patch.object(loader, '_load_from_file')
        load_from_file_spy = mocker.spy(loader, '_load_from_file')
        mocker.patch('tempfile.mkdtemp', return_value=tmp_path)
        config = loader.load()
        uri_to_local_spy.assert_has_calls([
          mocker.call(
            'file:///test/fixtures/template_config.yml',
            tmp_path,
            'hokusai.yml'
          )
        ])
        load_from_file_spy.assert_has_calls([
          mocker.call(
            os.path.join(tmp_path, 'hokusai.yml')
          )
        ])
      def it_catches_exceptions(mocker, mock_uri_to_local_raise):
        mocker.patch('hokusai.lib.config_loader.uri_to_local').side_effect = mock_uri_to_local_raise
        loader = ConfigLoader('file:///test/fixtures/template_config.yml')
        with pytest.raises(Exception):
          config = loader.load()
    def describe_other_type():
      def it_errors():
        loader = ConfigLoader('fooscheme://bar')
        with pytest.raises(HokusaiError):
          loader.load()
