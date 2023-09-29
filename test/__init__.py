import os
import boto3
import unittest


class HokusaiTestCase(unittest.TestCase):
  def fixture(self, filename):
    with open(os.path.join(os.getcwd(), 'test', 'fixtures', filename), 'r') as f:
      return f.read()

class HokusaiUnitTestCase(HokusaiTestCase):
  pass

class HokusaiIntegrationTestCase(HokusaiTestCase):
  pass

class HokusaiSmokeTestCase(HokusaiTestCase):
  pass


TEST_KUBE_CONTEXT = os.environ.get('HOKUSAI_TEST_KUBE_CTX', 'minikube')

for varname, varval in list(os.environ.items()):
  if 'HOKUSAI_' in varname:
    del os.environ[varname]

boto3.setup_default_session(aws_access_key_id='foo', aws_secret_access_key='bar')

if os.environ.get('DEBUG'):
  boto3.set_stream_logger(name='botocore')
