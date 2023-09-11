import os

import hokusai.services.command_runner

from hokusai.services.command_runner import CommandRunner
from hokusai.services.ecr import ECR

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
