import os

import hokusai.services.command_runner

from hokusai.services.command_runner import CommandRunner
from hokusai.services.ecr import ECR
from test.unit.test_services.fixtures.ecr import mock_ecr_class

def describe_command_runner():
  def describe_init():
    def it_inits(monkeypatch):
      monkeypatch.setenv('USER', 'foo')
      runner = CommandRunner('staging')
      assert runner.context == 'staging'
      assert type(runner.ecr) == ECR
      assert '-hokusai-run-foo' in runner.pod_name
      assert '-hokusai-run-foo' in runner.container_name
  def describe_name():
    def it_returns_name(mocker, monkeypatch):
      monkeypatch.setenv('USER', 'foo')
      runner = CommandRunner('staging')
      spy = mocker.spy(hokusai.services.command_runner, 'k8s_uuid')
      assert 'hello-hokusai-run-foo-' in runner._name()
      assert spy.call_count == 1
  def describe_image_name():
    def describe_separator_is_at_sign():
      def it_does_not_add_at_sign(mocker, mock_ecr_class):
        mocker.patch('hokusai.services.command_runner.ECR').side_effect = mock_ecr_class
        runner = CommandRunner('staging')
        assert runner._image_name('123') == 'foo:123'
    def describe_separator_is_colon():
      def it_adds_at_sign(mocker, mock_ecr_class):
        mocker.patch('hokusai.services.command_runner.ECR').side_effect = mock_ecr_class
        runner = CommandRunner('staging')
        assert runner._image_name('123:456') == 'foo@123:456'
  def describe_set_env():
    def it_sets():
      runner = CommandRunner('staging')
      spec = runner._set_env({}, ('foo=bar',))
      assert spec == {'env': [{'name': 'foo', 'value': 'bar'}]}
    def it_overwrites():
      runner = CommandRunner('staging')
      spec = {'env': [{'name': 'foo', 'value': 'bar'}]}
      spec = runner._set_env(spec, ('bar=foo',))
      assert spec == {'env': [{'name': 'bar', 'value': 'foo'}]}
  def describe_set_envfrom():
    def it_sets():
      runner = CommandRunner('staging')
      spec = runner._set_envfrom({})
      assert spec == {
        'envFrom': [
          {
            'configMapRef': {
              'name': 'hello-environment'
            }
          },
          {
            'secretRef': {
              'name': 'hello',
              'optional': True
            }
          }
        ]
      }
