import json
import pytest

import hokusai.services.service_account

from hokusai.services.service_account import ServiceAccount

from test.unit.test_services.fixtures.kubectl import mock_kubectl_obj
from test.unit.test_services.fixtures.service_account import mock_k8s_sa_json_string, mock_sa_spec


def describe_service_account():

  def describe_init():
    def it_instantiates(mocker, mock_kubectl_obj):
      mocker.patch('hokusai.services.service_account.Kubectl', return_value=mock_kubectl_obj)
      obj = ServiceAccount('staging', name='foosa')
      assert obj.context == 'staging'
      assert obj.kctl == mock_kubectl_obj
      assert obj.name == 'foosa'
      assert obj.object == {}
      assert obj.spec == {}

  def describe_apply():
    def it_calls_kctl_apply(mocker, monkeypatch, mock_kubectl_obj, mock_sa_spec):
      mocker.patch('hokusai.services.service_account.Kubectl', return_value=mock_kubectl_obj)
      mocker.patch('hokusai.services.service_account.write_temp_file', return_value='foofile')
      write_temp_file_spy = mocker.spy(hokusai.services.service_account, 'write_temp_file')
      mock_hokusai_tmp_dir = 'hokusaitmpdir'
      monkeypatch.setattr(hokusai.services.service_account, "HOKUSAI_TMP_DIR", mock_hokusai_tmp_dir)
      apply_spy = mocker.spy(mock_kubectl_obj, 'apply')
      obj = ServiceAccount('staging', name='foosa', spec=mock_sa_spec)
      obj.apply()
      write_temp_file_spy.assert_called_once_with(
        json.dumps(mock_sa_spec),
        mock_hokusai_tmp_dir
      )
      apply_spy.assert_called_once_with('foofile')

  def describe_load():
    def it_calls_loads(mocker, monkeypatch, mock_kubectl_obj, mock_k8s_sa_json_string, mock_sa_spec):
      mocker.patch('hokusai.services.service_account.Kubectl', return_value=mock_kubectl_obj)
      command_spy = mocker.spy(mock_kubectl_obj, 'command')
      mocker.patch('hokusai.services.service_account.shout', return_value=mock_k8s_sa_json_string)
      shout_spy = mocker.spy(hokusai.services.service_account, 'shout')
      obj = ServiceAccount('staging', name='foosa')
      obj.load()
      command_spy.assert_called_once_with(
        'get serviceaccount foosa -o json'
      )
      shout_spy.assert_called_once_with(
        'the command'
      )
      assert obj.object == json.loads(mock_k8s_sa_json_string)
      assert obj.spec == mock_sa_spec
