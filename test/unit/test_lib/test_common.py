import os

from hokusai.lib.common import user

def describe_user():
  def describe_user_not_set_in_env():
    def it_returns_none():
      del os.environ['USER']
      assert user() == None
  def describe_user_set_in_env():
    def it_returns_what_is_set():
      os.environ['USER'] = 'foo'
      assert user() == 'foo'
      os.environ['USER'] = ''
      assert user() == ''
    def it_replaces_upper_case_with_lower_case():
      os.environ['USER'] = 'FOO'
      assert user() == 'foo'
    def it_replaces_non_alpha_numeric_char_with_dash():
      os.environ['USER'] = 'foo.bar'
      assert user() == 'foo-bar'
      os.environ['USER'] = 'foo_bar'
      assert user() == 'foo-bar'
