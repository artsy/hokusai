import sys
if sys.version_info[0] >= 3:
  from unittest.mock import patch
else:
  from mock import patch

from test import HokusaiUnitTestCase
from test.utils import captured_output

from hokusai.lib.command import command
from hokusai.lib.exceptions import HokusaiError

@command()
def foo_command(foo):
  if foo:
    return 0
  else:
    raise ValueError('Bad command')

@command()
def error_command(msg):
  raise HokusaiError(msg, mask=(r'^(\w*).*$', r'\1 ***'))

class TestCommand(HokusaiUnitTestCase):
  @patch('hokusai.lib.command.sys.exit', return_code=True)
  def test_command_exits_with_return_code(self, mocked_sys_exit):
    foo_command('Ohai!')
    mocked_sys_exit.assert_called_once_with(0)

  @patch('hokusai.lib.command.sys.exit', return_code=True)
  def test_command_catches_exceptions(self, mocked_sys_exit):
    with captured_output() as (out, err):
      foo_command(False)
      mocked_sys_exit.assert_called_once_with(1)
      self.assertIn('ERROR: Bad command', out.getvalue().strip())

  @patch('hokusai.lib.command.sys.exit', return_code=True)
  def test_command_catches_masked_exceptions(self, mocked_sys_exit):
    with captured_output() as (out, err):
      error_command('Ohai!')
      mocked_sys_exit.assert_called_once_with(1)
      self.assertIn('ERROR: Ohai ***', out.getvalue().strip())
