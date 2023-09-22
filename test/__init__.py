import os
import unittest
import boto3

# these must be set before importing any hokusai module
os.environ['AWS_DEFAULT_REGION'] = 'foo-aws-region'
os.environ['HOME'] = os.path.join(os.getcwd(), 'test/fixtures/user')

from hokusai import CWD

from hokusai.lib import config

TEST_KUBE_CONTEXT = os.environ.get('HOKUSAI_TEST_KUBE_CTX', 'minikube')

for varname, varval in list(os.environ.items()):
  if 'HOKUSAI_' in varname:
    del os.environ[varname]

config.HOKUSAI_CONFIG_FILE = os.path.join(CWD, 'test/fixtures/project/hokusai/', 'config.yml')

boto3.setup_default_session(aws_access_key_id='foo', aws_secret_access_key='bar')

if os.environ.get('DEBUG'):
  boto3.set_stream_logger(name='botocore')

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
