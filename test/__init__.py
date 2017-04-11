import os
import unittest

from hokusai.common import shout, set_output
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
    set_output(False)
    if os.environ.get('DEBUG') is '1':
      print('Starting minikube...')
    shout('minikube start', print_output=os.environ.get('DEBUG') is '1')

  @classmethod
  def tearDownClass(cls):
    set_output(False)
    if os.environ.get('DEBUG') is '1':
      print('Deleting minikube...')
    shout('minikube delete', print_output=os.environ.get('DEBUG') is '1')
