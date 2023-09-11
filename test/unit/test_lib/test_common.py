import os
import pytest

from hokusai.lib.common import user, validate_env_var
from hokusai.lib.exceptions import HokusaiError

def describe_user():
  def describe_user_not_set_in_env():
    def it_returns_none(monkeypatch):
      monkeypatch.delenv('USER')
      assert user() == None
  def describe_user_set_in_env():
    def it_returns_what_is_set(monkeypatch):
      monkeypatch.setenv('USER', 'foo')
      assert user() == 'foo'
      monkeypatch.setenv('USER', '')
      assert user() == ''
    def it_replaces_upper_case_with_lower_case(monkeypatch):
      monkeypatch.setenv('USER', 'foo')
      assert user() == 'foo'
    def it_replaces_non_alpha_numeric_char_with_dash(monkeypatch):
      monkeypatch.setenv('USER', 'foo.bar')
      assert user() == 'foo-bar'
      monkeypatch.setenv('USER', 'foo_bar')
      assert user() == 'foo-bar'

def describe_validate_env_var():
  def describe_form_good():
    def it_does_not_error():
      validate_env_var('foo=bar')
  def describe_form_bad():
    def it_errors():
      with pytest.raises(HokusaiError):
        validate_env_var('foobar')
