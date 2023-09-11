import os

from hokusai.services.command_runner import CommandRunner
from hokusai.services.ecr import ECR

def describe_command_runner():
  def describe_init():
    def it_inits():
      os.environ['USER'] = 'foo'
      runner = CommandRunner('staging')
      assert runner.context == 'staging'
      assert type(runner.ecr) == ECR
      assert '-hokusai-run-foo' in runner.pod_name
      assert '-hokusai-run-foo' in runner.container_name
