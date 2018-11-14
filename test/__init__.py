import os
import unittest
import boto3

from hokusai.lib.common import shout
from hokusai.lib import config

config.HOKUSAI_CONFIG_FILE = os.path.join(os.getcwd(), 'test', 'fixtures', 'config.yml')

boto3.setup_default_session(aws_access_key_id='foo', aws_secret_access_key='bar')

if os.environ.get('DEBUG') is '1':
  boto3.set_stream_logger(name='botocore')

class HokusaiTestCase(unittest.TestCase):
  pass

class HokusaiUnitTestCase(HokusaiTestCase):
  pass

class HokusaiIntegrationTestCase(HokusaiTestCase):
  pass
