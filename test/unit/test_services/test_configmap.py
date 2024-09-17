import json
import pytest

import hokusai.services.configmap

from hokusai.lib.exceptions import HokusaiError
from hokusai.services.configmap import ConfigMap

from test.unit.test_services.fixtures.kubectl import mock_kubectl_obj
from test.unit.test_services.fixtures.configmap import expected_default_configmap_struct


def describe_configmap():

  def describe_init():
    def it_instantiates(mocker, mock_kubectl_obj, expected_default_configmap_struct):
      mocker.patch('hokusai.services.configmap.Kubectl', return_value=mock_kubectl_obj)
      obj = ConfigMap('staging')
      assert obj.context == 'staging'
      assert obj.kctl == mock_kubectl_obj
      assert obj.name == 'hello-environment'
      assert obj.struct == expected_default_configmap_struct

  def describe_all():
    def it_returns_data(mocker, mock_kubectl_obj):
      mocker.patch('hokusai.services.configmap.Kubectl', return_value=mock_kubectl_obj)
      obj = ConfigMap('staging')
      obj.struct['data'] = 'all my data'
      assert obj.all() == 'all my data'

  def describe_create():
    def it_calls_kctl_create(mocker, monkeypatch, mock_kubectl_obj, expected_default_configmap_struct):
      mocker.patch('hokusai.services.configmap.Kubectl', return_value=mock_kubectl_obj)
      mocker.patch('hokusai.services.configmap.write_temp_file', return_value='foofile')
      mock_hokusai_tmp_dir = 'hokusaitmpdir'
      monkeypatch.setattr(hokusai.services.configmap, "HOKUSAI_TMP_DIR", mock_hokusai_tmp_dir)
      write_temp_file_spy = mocker.spy(hokusai.services.configmap, 'write_temp_file')
      obj = ConfigMap('staging')
      create_spy = mocker.spy(mock_kubectl_obj, 'create')
      obj.create()
      create_spy.assert_called_once_with('foofile')
      write_temp_file_spy.assert_called_once_with(
        json.dumps(expected_default_configmap_struct),
        mock_hokusai_tmp_dir
      )

  def describe_delete():
    def describef_key_exists():
      def it_deletes(mocker):
        mocker.patch('hokusai.services.configmap.Kubectl', return_value=mock_kubectl_obj)
        obj = ConfigMap('staging')
        obj.struct['data']['fookey'] = 'foovalue'
        obj.delete('fookey')
        assert 'fookey' not in obj.struct
    def describef_key_non_existent():
      def it_raises(mocker):
        mocker.patch('hokusai.services.configmap.Kubectl', return_value=mock_kubectl_obj)
        obj = ConfigMap('staging')
        with pytest.raises(HokusaiError):
          obj.delete('fookey')


  def describe_destroy():
    def it_calls_kctl(mocker, mock_kubectl_obj):
      mocker.patch('hokusai.services.configmap.Kubectl', return_value=mock_kubectl_obj)
      command_spy = mocker.spy(mock_kubectl_obj, 'command')
      mocker.patch('hokusai.services.configmap.shout')
      shout_spy = mocker.spy(hokusai.services.configmap, 'shout')
      obj = ConfigMap('staging')
      obj.destroy()
      command_spy.assert_called_once_with(
        'delete configmap hello-environment'
      )
      shout_spy.assert_called_once_with(
        'the command',
        print_output=True
      )

  def describe_load():
    def describe_data_field_in_returned_configmap():
      def it_loads(mocker, mock_kubectl_obj):
        mocker.patch('hokusai.services.configmap.Kubectl', return_value=mock_kubectl_obj)
        command_spy = mocker.spy(mock_kubectl_obj, 'command')
        configmap_json_str = '{"data": {"foo_config": "foo_value"}}'
        configmap_json_struct = {
          'data': {
            'foo_config': 'foo_value'
          }
        }
        mocker.patch('hokusai.services.configmap.shout', return_value=configmap_json_str)
        obj = ConfigMap('staging')
        obj.load()
        command_spy.assert_called_once_with(
          'get configmap hello-environment -o json'
        )
        assert obj.struct['data'] == configmap_json_struct['data']
    def describe_no_data_field_in_returned_configmap():
      def it_assigns_empty_dict(mocker, mock_kubectl_obj):
        mocker.patch('hokusai.services.configmap.Kubectl', return_value=mock_kubectl_obj)
        configmap_json_str = '{"boguskey": "bogusvalue"}'
        mocker.patch('hokusai.services.configmap.shout', return_value=configmap_json_str)
        obj = ConfigMap('staging')
        obj.load()
        assert obj.struct['data'] == {}

  def describe_save():
    def it_saves(mocker, monkeypatch, mock_kubectl_obj, expected_default_configmap_struct):
      mocker.patch('hokusai.services.configmap.Kubectl', return_value=mock_kubectl_obj)
      mock_hokusai_tmp_dir = 'hokusaitmpdir'
      monkeypatch.setattr(hokusai.services.configmap, "HOKUSAI_TMP_DIR", mock_hokusai_tmp_dir)
      mocker.patch('hokusai.services.configmap.write_temp_file', return_value='foofile')
      apply_spy = mocker.spy(mock_kubectl_obj, 'apply')
      write_temp_file_spy = mocker.spy(hokusai.services.configmap, 'write_temp_file')
      obj = ConfigMap('staging')
      obj.save()
      write_temp_file_spy.assert_called_once_with(
        json.dumps(expected_default_configmap_struct),
        mock_hokusai_tmp_dir
      )
      apply_spy.assert_called_once_with('foofile')

  def describe_update():
    def it_updates(mocker, mock_kubectl_obj):
      mocker.patch('hokusai.services.configmap.Kubectl', return_value=mock_kubectl_obj)
      obj = ConfigMap('staging')
      obj.struct['data']['fookey'] = 'foovalue'
      obj.update('fookey', 'newfoovalue')
      assert obj.struct['data']['fookey'] == 'newfoovalue'
