import os
import unittest

if os.environ.get('DEBUG') is '1':
  import boto3
  boto3.set_stream_logger(name='botocore')

class HokusaiTestCase(unittest.TestCase):
  def setUp(self):
    super(HokusaiTestCase, self).setUp()

  def tearDown(self):
    super(HokusaiTestCase, self).tearDown()
