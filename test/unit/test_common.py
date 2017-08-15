import string

import yaml
from mock import patch

from test import HokusaiUnitTestCase
from test.utils import captured_output

from hokusai.lib.common import print_green, print_red, set_verbosity, verbose, returncode, shout, k8s_uuid, build_deployment, build_service

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

  def test_set_verbosity(self):
    set_verbosity(True)
    from hokusai.lib.common import VERBOSE
    self.assertEqual(VERBOSE, True)

  def test_verbose_returns_input(self):
    with captured_output() as (out, err):
      set_verbosity(True)
      msg = verbose(TEST_MESSAGE)
      self.assertEqual(msg, TEST_MESSAGE)

  def test_verbose_output(self):
    with captured_output() as (out, err):
      set_verbosity(True)
      verbose(TEST_MESSAGE)
      self.assertEqual(out.getvalue().strip(), "\x1b[33m==> hokusai exec `%s`\x1b[0m" % TEST_MESSAGE)

  def test_non_verbose_output(self):
    set_verbosity(False)
    with captured_output() as (out, err):
      verbose(TEST_MESSAGE)
      self.assertEqual(out.getvalue().strip(), '')

  def test_k8s_uuid(self):
    self.assertEqual(len(k8s_uuid()), 5)
    for char in list(k8s_uuid()):
      self.assertIn(char, string.lowercase)

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

  def test_build_deployment(self):
    basic_deployment = yaml.load(build_deployment('foo', 'nginx:latest', '80'))
    self.assertEqual(basic_deployment['kind'], 'Deployment')
    self.assertEqual(basic_deployment['apiVersion'], 'extensions/v1beta1')
    self.assertEqual(basic_deployment['metadata'], {'name': 'foo-web'})
    self.assertEqual(basic_deployment['spec']['template']['spec']['containers'], [{'image': 'nginx:latest', 'name': 'foo-web', 'envFrom': [{'configMapRef': {'name': 'foo-environment'}}], 'ports': [{'containerPort': '80'}]}])
    self.assertEqual(basic_deployment['spec']['template']['metadata'], {'labels': {'app': 'foo', 'layer': 'application', 'component': 'web'}, 'namespace': 'default', 'name': 'foo-web'})
    self.assertEqual(basic_deployment['spec']['replicas'], 1)
    self.assertEqual(basic_deployment['spec']['strategy'], {'rollingUpdate': { 'maxSurge': 1, 'maxUnavailable': 0 }, 'type': 'RollingUpdate'})

    replicated_deployment = yaml.load(build_deployment('foo', 'nginx:latest', '80', replicas=2))
    self.assertEqual(replicated_deployment['spec']['replicas'], 2)

    environmental_deployment = yaml.load(build_deployment('foo', 'nginx:latest', '80', environment={'FOO': 'BAR'}))
    self.assertEqual(environmental_deployment['spec']['template']['spec']['containers'], [{'image': 'nginx:latest', 'name': 'foo-web', 'env': {'FOO': 'BAR'}, 'envFrom': [{'configMapRef': {'name': 'foo-environment'}}], 'ports': [{'containerPort': '80'}]}])

    always_pulling_deployment = yaml.load(build_deployment('foo', 'nginx:latest', '80', always_pull=True))
    self.assertEqual(always_pulling_deployment['spec']['template']['spec']['containers'], [{'image': 'nginx:latest', 'imagePullPolicy': 'Always', 'envFrom': [{'configMapRef': {'name': 'foo-environment'}}], 'ports': [{'containerPort': '80'}], 'name': 'foo-web'}])

  def test_build_service(self):
    basic_service = yaml.load(build_service('foo', '80'))
    self.assertEqual(basic_service['kind'], 'Service')
    self.assertEqual(basic_service['apiVersion'], 'v1')
    self.assertEqual(basic_service['metadata'], {'labels': {'app': 'foo', 'layer': 'application', 'component': 'web'}, 'namespace': 'default', 'name': 'foo-web'})
    self.assertEqual(basic_service['spec'], {'type': 'ClusterIP', 'ports': [{'protocol': 'TCP', 'targetPort': '80', 'port': '80'}], 'selector': {'app': 'foo', 'layer': 'application', 'component': 'web'}})

    alternate_port_service = yaml.load(build_service('foo', '80', target_port='8080'))
    self.assertEqual(alternate_port_service['spec'], {'type': 'ClusterIP', 'ports': [{'protocol': 'TCP', 'targetPort': '8080', 'port': '80'}], 'selector': {'app': 'foo', 'layer': 'application', 'component': 'web'}})

    external_service = yaml.load(build_service('foo', '80', internal=False))
    self.assertEqual(external_service['spec'], {'type': 'LoadBalancer', 'sessionAffinity': 'None', 'ports': [{'protocol': 'TCP', 'targetPort': '80', 'port': '80'}], 'selector': {'app': 'foo', 'layer': 'application', 'component': 'web'}})
