import pytest

import hokusai.commands.push
from hokusai.commands.push import build_and_push, ecr_check, git_status_check, push_image, push_only, remote_tag_check, tag_and_push
from hokusai.lib.exceptions import HokusaiError

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

def describe_build_and_push():
  def it_builds_and_pushes(mocker):
    mocker.patch('hokusai.commands.push.Docker.build')
    mocker.patch('hokusai.commands.push.push_only')
    docker_build_spy = mocker.spy(hokusai.commands.push.Docker, 'build')
    push_only_spy = mocker.spy(hokusai.commands.push, 'push_only')
    args = {
      'remote_tag': 'remotefoo',
      'local_tag': 'localfoo',
      'filename': 'foofile',
      'ecr': None,
      'skip_latest': False
    }
    build_and_push(**args)
    assert docker_build_spy.call_count == 1
    assert push_only_spy.call_count == 1

def describe_ecr_check():
  def it_raises_when_repo_does_not_exist(mocker):
    class mock_ECR:
      def __init__(self):
        pass
      def project_repo_exists(self):
        return False
    mocker.patch('hokusai.commands.push.ECR').side_effect = mock_ECR
    with pytest.raises(HokusaiError):
      ecr_check()

  def it_returns_ecr_object_when_repo_exists(mocker):
    class mock_ECR:
      def __init__(self):
        pass
      def project_repo_exists(self):
        return True
    mocker.patch('hokusai.commands.push.ECR').side_effect = mock_ECR
    obj = ecr_check()
    assert isinstance(obj, mock_ECR)

def describe_git_status_check():
  def it_raises_if_working_dir_unclean(mocker):
    mocker.patch('hokusai.commands.push.shout', return_value='foo')
    with pytest.raises(HokusaiError):
      git_status_check()

  def it_does_not_raise_if_working_dir_is_clean(mocker):
    mocker.patch('hokusai.commands.push.shout', return_value=None)
    git_status_check()

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
    push_image(**args)
    assert build_and_push_spy.call_count == 0
    assert ecr_check_spy.call_count == 1
    assert git_status_check_spy.call_count == 0
    assert push_only_spy.call_count == 1
    assert remote_tag_check_spy.call_count == 1

def describe_push_only():
  class mock_ECR:
    def __init__(self):
      pass
    def get_login(self):
      pass
    def project_repo(self):
      pass

  def it_pushes_tag_and_latest(mocker):
    args = {
      'remote_tag': 'remotefoo',
      'local_tag': 'localfoo',
      'ecr': mock_ECR(),
      'skip_latest': False,
    }
    mocker.patch('hokusai.commands.push.shout')
    mocker.patch('hokusai.commands.push.tag_and_push')
    tag_and_push_spy = mocker.spy(hokusai.commands.push, 'tag_and_push')
    push_only(**args)
    assert tag_and_push_spy.call_count == 2

  def it_skips_latest_when_skip_latest_is_true(mocker):
    mock_ecr = mock_ECR()
    args = {
      'remote_tag': 'remotefoo',
      'local_tag': 'localfoo',
      'ecr': mock_ecr,
      'skip_latest': True,
    }
    mocker.patch('hokusai.commands.push.shout')
    mocker.patch('hokusai.commands.push.tag_and_push')
    tag_and_push_spy = mocker.spy(hokusai.commands.push, 'tag_and_push')
    push_only(**args)
    assert tag_and_push_spy.call_count == 1
    tag_and_push_spy.assert_has_calls([
      mocker.call(
        'hokusai_hello',
        'localfoo',
        mock_ecr.project_repo,
        'remotefoo'
      )
    ])

def describe_remote_tag_check():
  def describe_tag_does_not_exist_in_ecr():
    class mock_ECR:
      def __init__(self):
        pass
      def tag_exists(self, tag):
        return False

    def it_returns_same_tag_that_was_passed_in(mocker):
      mock_ecr = mock_ECR()
      mocker.patch('hokusai.commands.push.shout')
      tag = remote_tag_check(remote_tag='foo', overwrite=False, ecr=mock_ecr)
      assert tag == 'foo'

    def it_returns_git_head_sha_as_tag_when_none_was_passed_in(mocker):
      mock_ecr = mock_ECR()
      mocker.patch('hokusai.commands.push.shout', return_value='foo')
      tag = remote_tag_check(remote_tag=None, overwrite=False, ecr=mock_ecr)
      assert tag == 'foo'

  def describe_tag_exists_in_ecr():
    class mock_ECR:
      def __init__(self):
        pass
      def tag_exists(self, tag):
        return True

    def it_raises_if_tag_exists_in_ecr(mocker):
      mock_ecr = mock_ECR()
      mocker.patch('hokusai.commands.push.shout')
      with pytest.raises(HokusaiError):
        remote_tag_check(remote_tag='foo', overwrite=False, ecr=mock_ecr)

    def it_does_not_raise_if_tag_exists_in_ecr_and_overwrite_is_true(mocker):
      mock_ecr = mock_ECR()
      mocker.patch('hokusai.commands.push.shout')
      remote_tag_check(remote_tag='foo', overwrite=True, ecr=mock_ecr)

def describe_tag_and_push():
  def it_tags_and_pushes(mocker):
    mocker.patch('hokusai.commands.push.shout')
    shout_spy = mocker.spy(hokusai.commands.push, 'shout')
    tag_and_push('localfoorepo', 'localfootag', 'removefoorepo', 'remotefootag')
    shout_spy.assert_has_calls([
      mocker.call('docker tag localfoorepo:localfootag removefoorepo:remotefootag'),
      mocker.call('docker push removefoorepo:remotefootag', print_output=True)
    ])
