import string

from test import HokusaiTestCase
from test.utils import captured_output

import httpretty
from mock import patch

from hokusai.common import print_green, print_red, set_output, verbose, k8s_uuid, returncode, shout, get_ecr_login

TEST_MESSAGE = 'Ohai!'

httpretty.enable()
httpretty.HTTPretty.allow_net_connect = False

class TestCommon(HokusaiTestCase):
  def test_print_green(self):
    with captured_output() as (out, err):
      print_green(TEST_MESSAGE)
      self.assertEqual(out.getvalue().strip(), "\x1b[32m%s\x1b[0m" % TEST_MESSAGE)

  def test_print_red(self):
    with captured_output() as (out, err):
      print_red(TEST_MESSAGE)
      self.assertEqual(out.getvalue().strip(), "\x1b[31m%s\x1b[0m" % TEST_MESSAGE)

  def test_default_output(self):
    from hokusai.common import VERBOSE
    self.assertEqual(VERBOSE, False)

  def test_set_output(self):
    set_output(True)
    from hokusai.common import VERBOSE
    self.assertEqual(VERBOSE, True)

  def test_verbose_returns_input(self):
    with captured_output() as (out, err):
      set_output(True)
      msg = verbose(TEST_MESSAGE)
      self.assertEqual(msg, TEST_MESSAGE)

  def test_verbose_output(self):
    with captured_output() as (out, err):
      set_output(True)
      verbose(TEST_MESSAGE)
      self.assertEqual(out.getvalue().strip(), "\x1b[33m==> hokusai exec `%s`\x1b[0m" % TEST_MESSAGE)

  def test_non_verbose_output(self):
    set_output(False)
    with captured_output() as (out, err):
      verbose(TEST_MESSAGE)
      self.assertEqual(out.getvalue().strip(), '')

  def test_k8s_uuid(self):
    self.assertEqual(len(k8s_uuid()), 5)
    for char in list(k8s_uuid()):
      self.assertIn(char, string.lowercase)

  @patch('hokusai.common.check_output', return_value='hokusai')
  def test_shout(self, mocked_check_output):
    with captured_output() as (out, err):
      self.assertEqual(shout('whoami'), 'hokusai')
      mocked_check_output.assert_called_once_with('whoami', shell=True, stderr=-2)

  @patch('hokusai.common.check_call', return_value=0)
  def test_shout_returncode(self, mocked_check_call):
    with captured_output() as (out, err):
      self.assertEqual(shout('whoami', print_output=True), 0)
      mocked_check_call.assert_called_once_with('whoami', shell=True, stderr=-2)

  @patch('hokusai.common.call', return_value=0)
  def test_returncode(self, mocked_call):
    with captured_output() as (out, err):
      self.assertEqual(returncode('whoami'), 0)
      mocked_call.assert_called_once_with('whoami', shell=True, stderr=-2)

  @httpretty.activate
  def test_get_ecr_login(self):
    httpretty.register_uri(httpretty.POST, "https://ecr.us-east-1.amazonaws.com/",
                           body='{"authorizationData":[{"authorizationToken":"QVdTOjc2VzhZRVVGSERTQUU5OERGREhTRlNERklVSFNEQUpLR0tTQURGR0tERg==","expiresAt":1E9,"proxyEndpoint":"https://12345.dkr.ecr.us-east-1.amazonaws.com"}]}',
                           content_type="application/x-amz-json-1.1")
    self.assertEqual(get_ecr_login('12345'), 'docker login -u AWS -p 76W8YEUFHDSAE98DFDHSFSDFIUHSDAJKGKSADFGKDF -e none https://12345.dkr.ecr.us-east-1.amazonaws.com')
