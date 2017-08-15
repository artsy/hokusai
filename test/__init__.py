import os
import unittest

from hokusai.lib.common import shout
from hokusai.lib import config

config.HOKUSAI_CONFIG_FILE = os.path.join(os.getcwd(), 'test', 'fixtures', 'config.yml')

if os.environ.get('DEBUG') is '1':
  import boto3
  boto3.set_stream_logger(name='botocore')

class HokusaiTestCase(unittest.TestCase):
  pass

class HokusaiUnitTestCase(HokusaiTestCase):
  pass

class HokusaiIntegrationTestCase(HokusaiTestCase):
  pass
