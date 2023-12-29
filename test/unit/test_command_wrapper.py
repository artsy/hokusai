import sys
from unittest.mock import patch
from test import HokusaiUnitTestCase
from test.utils import captured_output

from hokusai.lib.command_wrapper import wrap

def foo_command(foo):
  if foo:
    return 0
  else:
    raise ValueError('Bad command')

class TestCommand(HokusaiUnitTestCase):
  @patch('hokusai.lib.command_wrapper.sys.exit', return_code=True)
  def test_command_exits_with_return_code(self, mocked_sys_exit):
    wrap(foo_command, 'Ohai!')
    mocked_sys_exit.assert_called_once_with(0)

  @patch('hokusai.lib.command_wrapper.sys.exit', return_code=True)
  def test_command_catches_exceptions(self, mocked_sys_exit):
    with captured_output() as (out, err):
      wrap(foo_command, False)
      mocked_sys_exit.assert_called_once_with(1)
      self.assertIn('Bad command', out.getvalue().strip())
