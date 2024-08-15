import json
import os
import pytest

from datetime import datetime
from pathlib import Path
from tempfile import NamedTemporaryFile

import hokusai.lib.common
import test.unit.test_lib.fixtures.common

from hokusai.lib.common import (
  ansi_escape,
  file_debug,
  get_platform,
  key_value_list_to_dict,
  local_to_local,
  uri_to_local,
  user,
  utc_yyyymmdd,
  validate_key_value
)
from hokusai.lib.exceptions import HokusaiError
from test.unit.test_lib.fixtures.common import (
  download_for_spy,
  mock_local_to_local_raise,
  mock_s3_interface_class
)


def describe_ansi_escape():
  def it_removes_color():
    green_foo = '\x1b[32mfoo\x1b[0m'
    assert ansi_escape(green_foo) == 'foo'

def describe_file_debug():
  def describe_when_debug_on():
    def it_writes_file(mocker, monkeypatch, tmp_path):
      d1 = {
        'foo': 'bar',
        'bar': 'foo'
      }
      tmp_file_obj = NamedTemporaryFile(delete=False, dir=tmp_path, mode='w')
      mocker.patch('hokusai.lib.common.NamedTemporaryFile', return_value=tmp_file_obj)
      monkeypatch.setenv('DEBUG', '1')
      file_debug(d1)
      with open(tmp_file_obj.name, 'r') as f:
        content = f.read().strip()
      assert json.loads(content) == d1
  def describe_when_debug_off():
    def it_does_not_write_file(mocker, monkeypatch, tmp_path):
      d1 = {
        'foo': 'bar',
        'bar': 'foo'
      }
      tmp_file_obj = NamedTemporaryFile(delete=False, dir=tmp_path, mode='w')
      mocker.patch('hokusai.lib.common.NamedTemporaryFile', return_value=tmp_file_obj)
      monkeypatch.setenv('DEBUG', '')
      file_debug(d1)
      with open(tmp_file_obj.name, 'r') as f:
        content = f.read().strip()
      with pytest.raises(json.decoder.JSONDecodeError):
        json.loads(content)

def describe_get_platform():
  def it_returns_platform(mocker):
    mocker.patch('hokusai.lib.common.platform.system', return_value='fooplatform')
    assert get_platform() == 'fooplatform'
  def it_returns_lower_case(mocker):
    mocker.patch('hokusai.lib.common.platform.system', return_value='FooPlatform')
    assert get_platform() == 'fooplatform'

def describe_key_value_list_to_dict():
  def it_transforms():
    kv_list = [
      'key1=value1',
      'key2=value2',
    ]
    assert key_value_list_to_dict(kv_list) == {
      'key1': 'value1',
      'key2': 'value2'
    }

def describe_local_to_local():
  def describe_source_exists():
    def describe_target_exists():
      def describe_it_is_a_dir():
        def it_errors(tmp_path):
          source = os.path.join(tmp_path, 'a.yml')
          spath = Path(source)
          spath.touch()
          target = os.path.join(tmp_path, 'foodir')
          tpath = Path(target)
          tpath.mkdir()
          with pytest.raises(HokusaiError):
            local_to_local(source, tmp_path, 'foodir')
      def describe_it_is_a_file():
        def it_backs_up_file_and_copies(tmp_path):
          source = os.path.join(tmp_path, 'a.yml')
          spath = Path(source)
          spath.touch()
          target = os.path.join(tmp_path, 'b.yml')
          tpath = Path(target)
          tpath.touch()
          utc_yyyymmdd = datetime.utcnow().strftime("%Y%m%d")
          backup = os.path.join(tmp_path, f'b.yml.backup.{utc_yyyymmdd}')
          bpath = Path(backup)
          local_to_local(source, tmp_path, 'b.yml')
          assert tpath.is_file()
          assert bpath.is_file()
    def describe_target_does_not_exist():
      def describe_target_dir_exists():
        def it_copies_and_sets_default_mode(tmp_path):
          source = os.path.join(tmp_path, 'a.yml')
          spath = Path(source)
          spath.touch()
          target = os.path.join(tmp_path, 'b.yml')
          local_to_local(source, tmp_path, 'b.yml')
          tpath = Path(target)
          assert tpath.is_file()
          assert os.stat(target).st_mode == int(0o100660) # the leading 10 means regular file
        def it_copies_and_sets_custom_mode(tmp_path):
          source = os.path.join(tmp_path, 'a.yml')
          spath = Path(source)
          spath.touch()
          target = os.path.join(tmp_path, 'b.yml')
          local_to_local(source, tmp_path, 'b.yml', mode=0o111)
          tpath = Path(target)
          assert tpath.is_file()
          assert os.stat(target).st_mode == int(0o100111) # the leading 10 means regular file
        def it_copies_to_home_dir(monkeypatch, tmp_path):
          source = os.path.join(tmp_path, 'a.yml')
          spath = Path(source)
          spath.touch()
          home_dir = os.path.join(tmp_path, 'myhome')
          monkeypatch.setenv('HOME', home_dir)
          target = os.path.join(home_dir, 'subdir', 'b.yml')
          local_to_local(source, '~/subdir', 'b.yml')
          tpath = Path(target)
          assert tpath.is_file()
          assert os.stat(target).st_mode == int(0o100660) # the leading 10 means regular file
      def describe_target_dir_missing():
        def describe_create_target_dir_true():
          def it_copies(tmp_path):
            source = os.path.join(tmp_path, 'a.yml')
            spath = Path(source)
            spath.touch()
            target = os.path.join(tmp_path, 'missing', 'b.yml')
            local_to_local(source, os.path.join(tmp_path, 'missing'), 'b.yml')
            tpath = Path(target)
            assert tpath.is_file()
        def describe_create_target_dir_false():
          def it_errors(tmp_path):
            source = os.path.join(tmp_path, 'a.yml')
            spath = Path(source)
            spath.touch()
            with pytest.raises(FileNotFoundError):
              local_to_local(source, os.path.join(tmp_path, 'missing'), 'b.yml', create_target_dir=False)
  def describe_source_non_existent():
    def it_errors(tmp_path):
      source = os.path.join(tmp_path, 'a.yml')
      with pytest.raises(FileNotFoundError):
        local_to_local(source, tmp_path, 'b.yml')

def describe_uri_to_local():
  def describe_s3_scheme():
    def it_calls_s3_interface_download(mocker, mock_s3_interface_class, tmp_path):
      mocker.patch('hokusai.lib.common.S3Interface').side_effect = mock_s3_interface_class
      s3_spy = mocker.spy(test.unit.test_lib.fixtures.common, 'download_for_spy')
      mocker.patch('hokusai.lib.common.local_to_local')
      local_to_local_spy = mocker.spy(hokusai.lib.common, 'local_to_local')
      mocker.patch('hokusai.lib.common.tempfile.mkdtemp', return_value=tmp_path)
      uri_to_local('s3://foobucket/bar/file.txt', tmp_path, 'file.txt')
      s3_spy.assert_has_calls([
        mocker.call(
          's3://foobucket/bar/file.txt',
          os.path.join(tmp_path, 'downloaded_file')
        )
      ])
      local_to_local_spy.assert_has_calls([
        mocker.call(
          os.path.join(tmp_path, 'downloaded_file'),
          tmp_path,
          'file.txt'
        )
      ])

  def describe_no_scheme():
    def it_calls_local_to_local(mocker):
      mocker.patch('hokusai.lib.common.local_to_local')
      spy = mocker.spy(hokusai.lib.common, 'local_to_local')
      uri_to_local('./foodir/source.txt', '/target_dir', 'target_file')
      spy.assert_has_calls([
        mocker.call(
          './foodir/source.txt',
          '/target_dir',
          'target_file'
        )
      ])
    def it_raises_if_error_downstream(mocker, mock_local_to_local_raise):
      mocker.patch('hokusai.lib.common.local_to_local').side_effect = mock_local_to_local_raise
      with pytest.raises(Exception):
        uri_to_local('file:///foodir/source.txt', '/target_dir', 'target_file')
  def describe_unsupported_scheme():
    def it_errors():
      with pytest.raises(HokusaiError):
        uri_to_local('foo://foodir/source.txt', '/target_dir', 'target_file')

def describe_user():
  def describe_user_not_set_in_env():
    def it_returns_none(monkeypatch):
      monkeypatch.delenv('USER', raising=False)
      assert user() == None
  def describe_user_set_in_env():
    def it_returns_what_is_set(monkeypatch):
      monkeypatch.setenv('USER', 'foo')
      assert user() == 'foo'
      monkeypatch.setenv('USER', '')
      assert user() == ''
    def it_replaces_upper_case_with_lower_case(monkeypatch):
      monkeypatch.setenv('USER', 'FOO')
      assert user() == 'foo'
    def it_replaces_non_alpha_numeric_char_with_dash(monkeypatch):
      monkeypatch.setenv('USER', 'foo.bar')
      assert user() == 'foo-bar'
      monkeypatch.setenv('USER', 'foo_bar')
      assert user() == 'foo-bar'

def describe_utc_yyyymmdd():
  def it_returns():
    assert utc_yyyymmdd() == datetime.utcnow().strftime("%Y%m%d")

def describe_validate_key_value():
  def describe_form_good():
    def it_returns_true():
      assert validate_key_value('foo=bar') == True
      assert validate_key_value('foo=bar=bing') == True
  def describe_form_bad():
    def it_raises():
      with pytest.raises(HokusaiError):
        validate_key_value('foobar')
