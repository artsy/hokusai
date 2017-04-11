import os
import unittest

from hokusai.common import shout
from hokusai import config

config.HOKUSAI_CONFIG_FILE = os.path.join(os.getcwd(), 'test', 'fixtures', 'config.yml')

if os.environ.get('DEBUG') is '1':
  import boto3
  boto3.set_stream_logger(name='botocore')

class HokusaiTestCase(unittest.TestCase):
  pass

class HokusaiUnitTestCase(HokusaiTestCase):
  pass

class HokusaiIntegrationTestCase(HokusaiTestCase):
  @classmethod
  def setUpClass(cls):
    shout('minikube start', print_output=True)

  @classmethod
  def tearDownClass(cls):
    shout('minikube destroy', print_output=True)
