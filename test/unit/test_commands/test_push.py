import pytest

import hokusai.commands.push
from hokusai.commands.push import push_image

def setup_spies(mocker):
  mocker.patch('hokusai.commands.push.build_and_push')
  mocker.patch('hokusai.commands.push.ecr_check', return_value='')
  mocker.patch('hokusai.commands.push.git_status_check')
  mocker.patch('hokusai.commands.push.push_only')
  mocker.patch('hokusai.commands.push.remote_tag_check', return_value='')
  build_and_push_spy = mocker.spy(hokusai.commands.push, 'build_and_push')
  ecr_check_spy = mocker.spy(hokusai.commands.push, 'ecr_check')
  git_status_check_spy = mocker.spy(hokusai.commands.push, 'git_status_check')
  push_only_spy = mocker.spy(hokusai.commands.push, 'push_only')
  remote_tag_check_spy = mocker.spy(hokusai.commands.push, 'remote_tag_check')
  return build_and_push_spy, ecr_check_spy, git_status_check_spy, push_only_spy, remote_tag_check_spy

def describe_push_image():
  def it_builds_when_build_is_true(mocker):
    build_and_push_spy, ecr_check_spy, git_status_check_spy, push_only_spy, remote_tag_check_spy = setup_spies(mocker)
    args = {
      'remote_tag': 'remotefoo',
      'local_tag': 'localfoo',
      'build': True,
      'filename': 'foofile',
      'force': False,
      'overwrite': False,
      'skip_latest': False,
    }
    with pytest.raises(SystemExit):
      push_image(**args)
    assert build_and_push_spy.call_count == 1
    assert ecr_check_spy.call_count == 1
    assert git_status_check_spy.call_count == 1
    assert push_only_spy.call_count == 0
    assert remote_tag_check_spy.call_count == 1

  def it_skips_build_when_build_is_false(mocker):
    build_and_push_spy, ecr_check_spy, git_status_check_spy, push_only_spy, remote_tag_check_spy = setup_spies(mocker)
    args = {
      'remote_tag': 'remotefoo',
      'local_tag': 'localfoo',
      'build': False,
      'filename': 'foofile',
      'force': False,
      'overwrite': False,
      'skip_latest': False,
    }
    with pytest.raises(SystemExit):
      push_image(**args)
    assert build_and_push_spy.call_count == 0
    assert ecr_check_spy.call_count == 1
    assert git_status_check_spy.call_count == 1
    assert push_only_spy.call_count == 1
    assert remote_tag_check_spy.call_count == 1

  def it_skips_git_status_check_when_force_is_true(mocker):
    build_and_push_spy, ecr_check_spy, git_status_check_spy, push_only_spy, remote_tag_check_spy = setup_spies(mocker)
    args = {
      'remote_tag': 'remotefoo',
      'local_tag': 'localfoo',
      'build': False,
      'filename': 'foofile',
      'force': True,
      'overwrite': False,
      'skip_latest': False,
    }
    with pytest.raises(SystemExit):
      push_image(**args)
    assert build_and_push_spy.call_count == 0
    assert ecr_check_spy.call_count == 1
    assert git_status_check_spy.call_count == 0
    assert push_only_spy.call_count == 1
    assert remote_tag_check_spy.call_count == 1
