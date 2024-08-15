import json
import os
import pipes
import pytest

import hokusai.services.command_runner

from hokusai.lib.exceptions import HokusaiError
from hokusai.services.command_runner import CommandRunner
from test.unit.test_services.fixtures.ecr import mock_ecr_class
from test.unit.test_services.fixtures.command_runner import (
  mock_clean_pod_spec,
  mock_overrides_spec,
  mock_pod_spec,
  mock_tty_spec,
)

HOKUSAI_TEMPLATE_FILE = 'test/fixtures/project/hokusai/hokusai_spec.yml'

def describe_command_runner():
  def describe_init():
    def describe_when_run_template_specified():
      def it_inits(mocker, monkeypatch, mock_ecr_class):
        mocker.patch('hokusai.services.command_runner.Kubectl')
        mocker.patch('hokusai.services.command_runner.ECR').side_effect = mock_ecr_class
        monkeypatch.setenv('USER', 'foouser')
        mocker.patch('hokusai.services.command_runner.k8s_uuid', return_value = 'abcde')
        mocker.patch(
          'hokusai.services.command_runner.TemplateSelector.get',
          return_value = HOKUSAI_TEMPLATE_FILE
        )
        runner = CommandRunner('staging')
        assert runner.context == 'staging'
        assert type(runner.ecr) == mock_ecr_class
        assert runner.pod_name == 'hello-hokusai-run-foouser-abcde'
        assert runner.container_name == 'hello-hokusai-run-foouser-abcde'
        assert runner.yaml_template == HOKUSAI_TEMPLATE_FILE
        assert runner.model_deployment == 'hello-web'
        assert runner.secrets_file == '/path/to/secrets/file'

  def describe_name():
    def describe_user_set_in_env():
      def it_returns_name(mocker, monkeypatch, mock_ecr_class):
        mocker.patch('hokusai.services.command_runner.Kubectl')
        mocker.patch('hokusai.services.command_runner.ECR').side_effect = mock_ecr_class
        monkeypatch.setenv('USER', 'foouser')
        mocker.patch('hokusai.services.command_runner.k8s_uuid', return_value = 'abcde')
        mocker.patch(
          'hokusai.services.command_runner.TemplateSelector.get',
          return_value = HOKUSAI_TEMPLATE_FILE
        )
        runner = CommandRunner('staging')
        spy = mocker.spy(hokusai.services.command_runner, 'k8s_uuid')
        assert runner._name() == 'hello-hokusai-run-foouser-abcde'
        assert spy.call_count == 1
    def describe_user_unset_in_env():
      def it_returns_name(mocker, monkeypatch, mock_ecr_class):
        mocker.patch('hokusai.services.command_runner.Kubectl')
        mocker.patch('hokusai.services.command_runner.ECR').side_effect = mock_ecr_class
        monkeypatch.delenv('USER', raising=False)
        mocker.patch('hokusai.services.command_runner.k8s_uuid', return_value = 'abcde')
        mocker.patch(
          'hokusai.services.command_runner.TemplateSelector.get',
          return_value = HOKUSAI_TEMPLATE_FILE
        )
        runner = CommandRunner('staging')
        spy = mocker.spy(hokusai.services.command_runner, 'k8s_uuid')
        assert runner._name() == 'hello-hokusai-run-abcde'
        assert spy.call_count == 1

  def describe_image_name():
    def describe_tag_has_no_colon():
      def it_uses_colon_as_separator(mocker, mock_ecr_class):
        mocker.patch('hokusai.services.command_runner.Kubectl')
        mocker.patch('hokusai.services.command_runner.ECR').side_effect = mock_ecr_class
        mocker.patch('hokusai.services.command_runner.k8s_uuid', return_value = 'abcde')
        mocker.patch(
          'hokusai.services.command_runner.TemplateSelector.get',
          return_value = HOKUSAI_TEMPLATE_FILE
        )
        runner = CommandRunner('staging')
        assert runner._image_name('123') == 'foo:123'
    def describe_tag_has_colon():
      def it_uses_at_sign_as_separator(mocker, mock_ecr_class):
        mocker.patch('hokusai.services.command_runner.Kubectl')
        mocker.patch('hokusai.services.command_runner.ECR').side_effect = mock_ecr_class
        mocker.patch('hokusai.services.command_runner.k8s_uuid', return_value = 'abcde')
        mocker.patch(
          'hokusai.services.command_runner.TemplateSelector.get',
          return_value = HOKUSAI_TEMPLATE_FILE
        )
        runner = CommandRunner('staging')
        assert runner._image_name('123:456') == 'foo@123:456'

  def describe_overrides():
    def it_generates_spec(mocker, mock_ecr_class, mock_clean_pod_spec, mock_overrides_spec, monkeypatch):
      mocker.patch('hokusai.services.command_runner.Kubectl')
      monkeypatch.setenv('USER', 'foouser')
      mocker.patch('hokusai.services.command_runner.ECR').side_effect = mock_ecr_class
      mocker.patch('hokusai.services.command_runner.k8s_uuid', return_value = 'abcde')
      mocker.patch(
        'hokusai.services.command_runner.TemplateSelector.get',
        return_value = HOKUSAI_TEMPLATE_FILE
      )
      runner = CommandRunner('staging')
      spec = runner._overrides(
        'foocmd',
        ('fooconstraint=bar',),
        ('foo=bar',),
        'footag',
        mock_clean_pod_spec
      )
      assert spec == mock_overrides_spec

  def describe_run_no_tty():
    def it_runs(mocker, mock_ecr_class, mock_overrides_spec, monkeypatch):
      mocker.patch('hokusai.services.command_runner.Kubectl')
      monkeypatch.setenv('USER', 'foouser')
      mocker.patch('hokusai.services.command_runner.ECR').side_effect = mock_ecr_class
      mocker.patch('hokusai.services.command_runner.k8s_uuid', return_value = 'abcde')
      mocker.patch(
        'hokusai.services.command_runner.TemplateSelector.get',
        return_value = HOKUSAI_TEMPLATE_FILE
      )
      mocker.patch('hokusai.services.command_runner.returncode', return_value=0)
      runner = CommandRunner('staging')
      spy = mocker.spy(runner.kctl, 'command')
      runner._run_no_tty('foocmd', 'imagex', mock_overrides_spec)
      spy.assert_has_calls([
        mocker.call(
          f'run hello-hokusai-run-foouser-abcde --attach --image=imagex ' +
          f'--overrides={pipes.quote(json.dumps(mock_overrides_spec))} ' +
          '--restart=Never --rm'
        )
      ])

  def describe_run_tty():
    def it_runs(mocker, mock_ecr_class, mock_tty_spec, monkeypatch):
      mocker.patch('hokusai.services.command_runner.Kubectl')
      monkeypatch.setenv('USER', 'foouser')
      mocker.patch('hokusai.services.command_runner.ECR').side_effect = mock_ecr_class
      mocker.patch('hokusai.services.command_runner.k8s_uuid', return_value = 'abcde')
      mocker.patch('hokusai.services.command_runner.shout', return_value=0)
      mocker.patch(
        'hokusai.services.command_runner.TemplateSelector.get',
        return_value = HOKUSAI_TEMPLATE_FILE
      )
      runner = CommandRunner('staging')
      spy = mocker.spy(runner.kctl, 'command')
      runner._run_tty('foocmd', 'imagex', mock_tty_spec)
      spy.assert_has_calls([
        mocker.call(
          f'run hello-hokusai-run-foouser-abcde -t -i --image=imagex ' +
          f'--restart=Never ' +
          f'--overrides={pipes.quote(json.dumps(mock_tty_spec))} ' +
          f'--rm'
        )
      ])

  def describe_run():
    def describe_tty():
      def it_runs(mocker, mock_ecr_class, mock_overrides_spec, monkeypatch):
        mocker.patch('hokusai.services.command_runner.Kubectl')
        monkeypatch.setenv('USER', 'foouser')
        mocker.patch('hokusai.services.command_runner.ECR').side_effect = mock_ecr_class
        mocker.patch('hokusai.services.command_runner.k8s_uuid', return_value = 'abcde')
        mocker.patch(
          'hokusai.services.command_runner.TemplateSelector.get',
          return_value = HOKUSAI_TEMPLATE_FILE
        )
        mocker.patch('hokusai.services.command_runner.YamlSpec')
        runner = CommandRunner('staging')
        mocker.patch.object(runner, '_run_tty')
        mocker.patch.object(runner, '_clean_pod_spec')
        mocker.patch.object(runner, '_overrides', return_value=mock_overrides_spec)
        spy = mocker.spy(runner, '_run_tty')
        runner.run('footag', 'foocmd', tty=True, env=('foo=bar',), constraint=('fooconstraint=bar',))
        assert spy.call_count == 1
        spy.assert_has_calls([
          mocker.call(
            'foocmd',
            'foo:footag',
            mock_overrides_spec
          )
        ])
    def describe_no_tty():
      def it_runs(mocker, mock_ecr_class, mock_overrides_spec, monkeypatch):
        mocker.patch('hokusai.services.command_runner.Kubectl')
        monkeypatch.setenv('USER', 'foouser')
        mocker.patch('hokusai.services.command_runner.ECR').side_effect = mock_ecr_class
        mocker.patch('hokusai.services.command_runner.k8s_uuid', return_value = 'abcde')
        mocker.patch(
          'hokusai.services.command_runner.TemplateSelector.get',
          return_value = HOKUSAI_TEMPLATE_FILE
        )
        mocker.patch('hokusai.services.command_runner.YamlSpec')
        runner = CommandRunner('staging')
        mocker.patch.object(runner, '_run_no_tty', return_value=0)
        mocker.patch.object(runner, '_clean_pod_spec')
        mocker.patch.object(runner, '_overrides', return_value=mock_overrides_spec)
        spy = mocker.spy(runner, '_run_no_tty')
        returncode = runner.run('footag', 'foocmd', tty=False, env=('foo=bar',), constraint=('fooconstraint=bar',))
        assert spy.call_count == 1
        spy.assert_has_calls([
          mocker.call(
            'foocmd',
            'foo:footag',
            mock_overrides_spec
          )
        ])
        assert returncode == 0
