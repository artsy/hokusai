import os
import unittest
import boto3

from hokusai import CWD
from hokusai.lib import config

TEST_KUBE_CONTEXT = os.environ.get('HOKUSAI_TEST_KUBE_CTX', 'minikube')

config.HOKUSAI_CONFIG_FILE = os.path.join(CWD, 'test/fixtures/project/hokusai/', 'config.yml')

boto3.setup_default_session(aws_access_key_id='foo', aws_secret_access_key='bar')

if os.environ.get('DEBUG') is '1':
  boto3.set_stream_logger(name='botocore')

class HokusaiTestCase(unittest.TestCase):
  pass

class HokusaiUnitTestCase(HokusaiTestCase):
  pass

class HokusaiIntegrationTestCase(HokusaiTestCase):
  pass
