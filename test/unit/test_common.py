import string

import yaml
from mock import patch

from test import HokusaiUnitTestCase
from test.utils import captured_output, mock_verbosity

from hokusai.lib.common import print_green, print_red, verbose, returncode, shout, k8s_uuid

TEST_MESSAGE = 'Ohai!'

class TestCommon(HokusaiUnitTestCase):
  def test_print_green(self):
    with captured_output() as (out, err):
      print_green(TEST_MESSAGE)
      self.assertEqual(out.getvalue().strip(), "\x1b[32m%s\x1b[0m" % TEST_MESSAGE)

  def test_print_red(self):
    with captured_output() as (out, err):
      print_red(TEST_MESSAGE)
      self.assertEqual(out.getvalue().strip(), "\x1b[31m%s\x1b[0m" % TEST_MESSAGE)

  def test_default_output(self):
    from hokusai.lib.common import VERBOSE
    self.assertEqual(VERBOSE, False)

  def test_verbose_returns_input(self):
    with mock_verbosity(True):
      with captured_output() as (out, err):
        msg = verbose(TEST_MESSAGE)
        self.assertEqual(msg, TEST_MESSAGE)

  def test_verbose_output(self):
    with mock_verbosity(True):
      with captured_output() as (out, err):
        verbose(TEST_MESSAGE)
        self.assertEqual(out.getvalue().strip(), "\x1b[33m==> hokusai exec `%s`\n\x1b[0m" % TEST_MESSAGE)

  def test_masked_verbose_output(self):
    with mock_verbosity(True):
      with captured_output() as (out, err):
        verbose(TEST_MESSAGE, mask=(r'^(\w*).*$', r'\1 ***'))
        self.assertEqual(out.getvalue().strip(), "\x1b[33m==> hokusai exec `%s`\n\x1b[0m" % 'Ohai ***')

  def test_non_verbose_output(self):
    with mock_verbosity(False):
      with captured_output() as (out, err):
        verbose(TEST_MESSAGE)
        self.assertEqual(out.getvalue().strip(), '')

  def test_k8s_uuid(self):
    self.assertEqual(len(k8s_uuid()), 5)
    for char in list(k8s_uuid()):
      self.assertIn(char, string.ascii_lowercase)

  @patch('hokusai.lib.common.check_output', return_value='hokusai')
  def test_shout(self, mocked_check_output):
    with captured_output() as (out, err):
      self.assertEqual(shout('whoami'), 'hokusai')
      mocked_check_output.assert_called_once_with('whoami', shell=True, stderr=-2)

  @patch('hokusai.lib.common.check_call', return_value=0)
  def test_shout_returncode(self, mocked_check_call):
    with captured_output() as (out, err):
      self.assertEqual(shout('whoami', print_output=True), 0)
      mocked_check_call.assert_called_once_with('whoami', shell=True, stderr=-2)

  @patch('hokusai.lib.common.call', return_value=0)
  def test_returncode(self, mocked_call):
    with captured_output() as (out, err):
      self.assertEqual(returncode('whoami'), 0)
      mocked_call.assert_called_once_with('whoami', shell=True, stderr=-2)
