import json
import os
import pipes
import pytest

import hokusai.services.command_runner

from hokusai.lib.exceptions import HokusaiError
from hokusai.services.command_runner import CommandRunner
from hokusai.services.ecr import ECR
from test.unit.test_services.fixtures.ecr import mock_ecr_class
from test.unit.test_services.fixtures.command_runner import (
  mock_spec,
  mock_tty_spec
)

def describe_command_runner():
  def describe_init():
    def it_inits(mocker, monkeypatch):
      monkeypatch.setenv('USER', 'foo')
      mocker.patch('hokusai.services.command_runner.k8s_uuid', return_value = 'abcde')
      runner = CommandRunner('staging')
      assert runner.context == 'staging'
      assert type(runner.ecr) == ECR
      assert runner.pod_name == 'hello-hokusai-run-foo-abcde'
      assert runner.container_name == 'hello-hokusai-run-foo-abcde'

  def describe_name():
    def describe_user_set_in_env():
      def it_returns_name(mocker, monkeypatch):
        monkeypatch.setenv('USER', 'foo')
        mocker.patch('hokusai.services.command_runner.k8s_uuid', return_value = 'abcde')
        runner = CommandRunner('staging')
        spy = mocker.spy(hokusai.services.command_runner, 'k8s_uuid')
        assert runner._name() == 'hello-hokusai-run-foo-abcde'
        assert spy.call_count == 1
    def describe_user_unset_in_env():
      def it_returns_name(mocker, monkeypatch):
        monkeypatch.delenv('USER', raising=False)
        mocker.patch('hokusai.services.command_runner.k8s_uuid', return_value = 'abcde')
        runner = CommandRunner('staging')
        spy = mocker.spy(hokusai.services.command_runner, 'k8s_uuid')
        assert runner._name() == 'hello-hokusai-run-abcde'
        assert spy.call_count == 1

  def describe_image_name():
    def describe_tag_has_no_colon():
      def it_uses_colon_as_separator(mocker, mock_ecr_class):
        mocker.patch('hokusai.services.command_runner.ECR').side_effect = mock_ecr_class
        runner = CommandRunner('staging')
        assert runner._image_name('123') == 'foo:123'
    def describe_tag_has_colon():
      def it_uses_at_sign_as_separator(mocker, mock_ecr_class):
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
    def it_raises_on_bad_form():
      with pytest.raises(HokusaiError):
        runner = CommandRunner('staging')
        runner._set_env({}, ('foo bar',))

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

  def describe_set_constraint():
    def it_sets():
      runner = CommandRunner('staging')
      spec = runner._set_constraint({}, ('foo=bar',))
      assert spec == {'nodeSelector': {'foo': 'bar'}}
    def it_overwrites():
      runner = CommandRunner('staging')
      spec = {'nodeSelector': {'foo': 'bar'}}
      spec = runner._set_constraint(spec, ('bar=foo',))
      assert spec == {'nodeSelector': {'bar': 'foo'}}
    def it_raises_on_bad_form():
      with pytest.raises(HokusaiError):
        runner = CommandRunner('staging')
        runner._set_constraint({}, ('foo bar',))

  def describe_overrides_container():
    def it_generates_spec(mocker, mock_ecr_class, mock_spec):
      mocker.patch('hokusai.services.command_runner.ECR').side_effect = mock_ecr_class
      mocker.patch('hokusai.services.command_runner.k8s_uuid', return_value = 'abcde')
      runner = CommandRunner('staging')
      spec = runner._overrides_container('foocmd', ('foo=bar',), 'footag')
      assert spec == mock_spec['spec']['containers'][0]

  def describe_overrrides_containers():
    def it_generates_spec(mocker, mock_ecr_class, mock_spec):
      mocker.patch('hokusai.services.command_runner.ECR').side_effect = mock_ecr_class
      mocker.patch('hokusai.services.command_runner.k8s_uuid', return_value = 'abcde')
      runner = CommandRunner('staging')
      spec = runner._overrrides_containers('foocmd', ('foo=bar',), 'footag')
      assert spec == mock_spec['spec']['containers']

  def describe_overrides_spec():
    def it_generates_spec(mocker, mock_ecr_class, mock_spec):
      mocker.patch('hokusai.services.command_runner.ECR').side_effect = mock_ecr_class
      mocker.patch('hokusai.services.command_runner.k8s_uuid', return_value = 'abcde')
      runner = CommandRunner('staging')
      spec = runner._overrides_spec('foocmd', ('fooconstraint=bar',), ('foo=bar',), 'footag')
      assert spec == mock_spec['spec']

  def describe_overrides():
    def it_generates_spec(mocker, mock_ecr_class, mock_spec):
      mocker.patch('hokusai.services.command_runner.ECR').side_effect = mock_ecr_class
      mocker.patch('hokusai.services.command_runner.k8s_uuid', return_value = 'abcde')
      runner = CommandRunner('staging')
      spec = runner._overrides('foocmd', ('fooconstraint=bar',), ('foo=bar',), 'footag')
      assert spec == mock_spec

  def describe_run_no_tty():
    def it_runs(mocker, mock_ecr_class, mock_spec, monkeypatch):
      monkeypatch.setenv('USER', 'foo')
      mocker.patch('hokusai.services.command_runner.k8s_uuid', return_value = 'abcde')
      mocker.patch('hokusai.services.command_runner.ECR').side_effect = mock_ecr_class
      mocker.patch('hokusai.services.command_runner.returncode', return_value=0)
      runner = CommandRunner('staging')
      spy = mocker.spy(runner.kctl, 'command')
      runner._run_no_tty('foocmd', 'imagex', mock_spec)
      spy.assert_has_calls([
        mocker.call(
          f'run hello-hokusai-run-foo-abcde --attach --image=imagex ' +
          f'--overrides={pipes.quote(json.dumps(mock_spec))} ' +
          '--restart=Never --rm'
        )
      ])

  def describe_run_tty():
    def it_runs(mocker, mock_ecr_class, mock_tty_spec, monkeypatch):
      monkeypatch.setenv('USER', 'foo')
      mocker.patch('hokusai.services.command_runner.k8s_uuid', return_value = 'abcde')
      mocker.patch('hokusai.services.command_runner.ECR').side_effect = mock_ecr_class
      mocker.patch('hokusai.services.command_runner.shout', return_value=0)
      runner = CommandRunner('staging')
      spy = mocker.spy(runner.kctl, 'command')
      runner._run_tty('foocmd', 'imagex', mock_tty_spec)
      spy.assert_has_calls([
        mocker.call(
          f'run hello-hokusai-run-foo-abcde -t -i --image=imagex ' +
          f'--restart=Never ' +
          f'--overrides={pipes.quote(json.dumps(mock_tty_spec))} ' +
          f'--rm'
        )
      ])

  def describe_run():
    def describe_tty():
      def it_runs(mocker, mock_ecr_class, mock_spec):
        mocker.patch('hokusai.services.command_runner.k8s_uuid', return_value = 'abcde')
        mocker.patch('hokusai.services.command_runner.ECR').side_effect = mock_ecr_class
        runner = CommandRunner('staging')
        mocker.patch.object(runner, '_run_tty')
        spy = mocker.spy(runner, '_run_tty')
        runner.run('footag', 'foocmd', tty=True, env=('foo=bar',), constraint=('fooconstraint=bar',))
        assert spy.call_count == 1
        spy.assert_has_calls([
          mocker.call(
            'foocmd',
            'foo:footag',
            mock_spec
          )
        ])
    def describe_no_tty():
      def it_runs(mocker, mock_ecr_class, mock_spec):
        mocker.patch('hokusai.services.command_runner.k8s_uuid', return_value = 'abcde')
        mocker.patch('hokusai.services.command_runner.ECR').side_effect = mock_ecr_class
        runner = CommandRunner('staging')
        mocker.patch.object(runner, '_run_no_tty')
        spy = mocker.spy(runner, '_run_no_tty')
        runner.run('footag', 'foocmd', tty=False, env=('foo=bar',), constraint=('fooconstraint=bar',))
        assert spy.call_count == 1
        spy.assert_has_calls([
          mocker.call(
            'foocmd',
            'foo:footag',
            mock_spec
          )
        ])
