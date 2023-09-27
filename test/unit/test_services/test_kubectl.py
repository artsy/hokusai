import json
import yaml

import hokusai.services.kubectl

from hokusai.services.kubectl import Kubectl
from test.unit.test_services.fixtures.kubectl import mock_shout_raises


def describe_kubectl():

  def describe_init():
    def it_instantiates(mocker):
      obj = Kubectl('staging')
      assert obj.context == 'staging'
      assert obj.namespace == None
      assert obj.kubectl == '/tmp/.local/bin/kubectl'

  def describe_command():
    def describe_without_namespace():
      def it_returns_correct_command():
        obj = Kubectl('staging')
        expected = "/tmp/.local/bin/kubectl --context staging foocommand"
        assert obj.command('foocommand') == expected
    def describe_with_namespace():
      def it_returns_correct_command():
        obj = Kubectl('staging', 'foonamespace')
        expected = "/tmp/.local/bin/kubectl --context staging --namespace foonamespace foocommand"
        assert obj.command('foocommand') == expected

  def describe_contexts():
    def it_returns_contexts(mocker):
      obj = Kubectl('staging')
      mock_contexts = {
        'contexts': [
          { 'name': 'context1' },
          { 'name': 'context2' },
          { 'name': 'context3' }
        ]
      }
      payload = yaml.safe_dump(mock_contexts, default_flow_style=False)
      mocker.patch('hokusai.services.kubectl.shout', return_value=payload)
      assert obj.contexts() == ['context1', 'context2', 'context3']

  def describe_get_object():
    def describe_no_error():
      def it_returns_output(mocker):
        obj = Kubectl('staging')
        mock_return = { 'foo': 'bar' }
        mocker.patch('hokusai.services.kubectl.shout', return_value=json.dumps(mock_return))
        assert obj.get_object('pods') == mock_return
    def describe_value_error():
      def it_returns_none(mocker, mock_shout_raises):
        obj = Kubectl('staging')
        mocker.patch('hokusai.services.kubectl.shout').side_effect = mock_shout_raises
        assert obj.get_object('pods') == None

  def describe_get_objects():
    def describe_no_error():
      def describe_with_selectors():
        def describe_no_error():
          def it_returns_data(mocker):
            obj = Kubectl('staging')
            mock_return = {
              'items': {
                  'foo': 'bar'
              }
            }
            mocker.patch('hokusai.services.kubectl.shout', return_value=json.dumps(mock_return))
            spy = mocker.spy(hokusai.services.kubectl, 'shout')
            assert obj.get_objects('pods', 'app=foo,layer=bar') == mock_return['items']
            spy.assert_has_calls([
              mocker.call(
                '/tmp/.local/bin/kubectl --context staging get pods --selector app=foo,layer=bar -o json'
              )
            ])
      def describe_without_selectors():
        def describe_no_error():
          def it_returns_data(mocker):
            obj = Kubectl('staging')
            mock_return = {
              'items': {
                  'foo': 'bar'
              }
            }
            mocker.patch('hokusai.services.kubectl.shout', return_value=json.dumps(mock_return))
            spy = mocker.spy(hokusai.services.kubectl, 'shout')
            assert obj.get_objects('pods') == mock_return['items']
            spy.assert_has_calls([
              mocker.call(
                '/tmp/.local/bin/kubectl --context staging get pods -o json'
              )
            ])
    def describe_value_error():
      def it_returns_empty_list(mocker, mock_shout_raises):
        obj = Kubectl('staging')
        mocker.patch('hokusai.services.kubectl.shout').side_effect = mock_shout_raises
        assert obj.get_objects('pods') == []
