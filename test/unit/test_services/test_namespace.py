import json
import pytest

import hokusai.services.namespace

from hokusai.lib.exceptions import HokusaiError
from hokusai.services.namespace import Namespace

from test.unit.test_services.fixtures.kubectl import mock_kubectl_obj
from test.unit.test_services.fixtures.namespace import expected_namespace_struct


def describe_namespace():

  def describe_init():
    def it_instantiates(mocker, mock_kubectl_obj):
      mocker.patch('hokusai.services.namespace.Kubectl', return_value=mock_kubectl_obj)
      obj = Namespace('staging', 'foons')
      assert obj.context == 'staging'
      assert obj.kctl == mock_kubectl_obj
      assert obj.name == 'foons'
      assert obj.labels == {}
      assert obj.struct == {}

  def describe_create():
    def describe_namespace_is_other():
      def it_calls_kctl_apply(mocker, monkeypatch, mock_kubectl_obj, expected_namespace_struct):
        mocker.patch('hokusai.services.namespace.Kubectl', return_value=mock_kubectl_obj)
        mocker.patch('hokusai.services.namespace.write_temp_file', return_value='foofile')
        mock_hokusai_tmp_dir = 'hokusaitmpdir'
        monkeypatch.setattr(hokusai.services.namespace, "HOKUSAI_TMP_DIR", mock_hokusai_tmp_dir)
        write_temp_file_spy = mocker.spy(hokusai.services.namespace, 'write_temp_file')
        obj = Namespace('staging', 'foons')
        apply_spy = mocker.spy(mock_kubectl_obj, 'apply')
        obj.create()
        apply_spy.assert_called_once_with('foofile')
        write_temp_file_spy.assert_called_once_with(
          json.dumps(expected_namespace_struct),
          mock_hokusai_tmp_dir
        )
    def describe_namespace_is_default():
      def it_raises(mocker, mock_kubectl_obj):
        mocker.patch('hokusai.services.namespace.Kubectl', return_value=mock_kubectl_obj)
        obj = Namespace('staging', 'default')
        apply_spy = mocker.spy(mock_kubectl_obj, 'apply')
        with pytest.raises(HokusaiError):
          obj.create()
          assert not apply_spy.called

  def describe_delete():
    def describe_namespace_is_other():
      def it_calls_shout(mocker, mock_kubectl_obj):
        mocker.patch('hokusai.services.namespace.Kubectl', return_value=mock_kubectl_obj)
        mocker.patch.object(mock_kubectl_obj, 'command', return_value='kubectl --context staging delete ns foons')
        command_spy = mocker.spy(mock_kubectl_obj, 'command')
        mocker.patch('hokusai.services.namespace.shout')
        shout_spy = mocker.spy(hokusai.services.namespace, 'shout')
        obj = Namespace('staging', 'foons')
        obj.delete()
        command_spy.assert_called_once_with(
          'delete namespace foons'
        )
        shout_spy.assert_called_once_with(
          'kubectl --context staging delete ns foons'
        )
    def describe_namespace_is_default():
      def it_raises(mocker, mock_kubectl_obj):
        mocker.patch('hokusai.services.namespace.Kubectl', return_value=mock_kubectl_obj)
        mocker.patch('hokusai.services.namespace.shout')
        shout_spy = mocker.spy(hokusai.services.namespace, 'shout')
        obj = Namespace('staging', 'default')
        with pytest.raises(HokusaiError):
          obj.delete()
          assert not shout_spy.called
