from mock import patch

from test import HokusaiUnitTestCase
from test.utils import captured_output

from hokusai.command import command

@command
def foo_command(foo):
  if foo:
    return 0
  else:
    raise ValueError('Bad command')

class TestCommand(HokusaiUnitTestCase):
  @patch('hokusai.command.sys.exit', retval=True)
  def test_command_exits_with_retval(self, mocked_sys_exit):
    foo_command('Ohai!')
    mocked_sys_exit.assert_called_once_with(0)

  @patch('hokusai.command.sys.exit', retval=True)
  def test_command_catches_exceptions(self, mocked_sys_exit):
    with captured_output() as (out, err):
      foo_command(False)
      mocked_sys_exit.assert_called_once_with(-1)
      self.assertEqual(out.getvalue().strip(), '\x1b[31mERROR: Bad command\x1b[0m')
