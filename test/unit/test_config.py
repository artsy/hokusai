import os

from hokusai.lib import config
from hokusai.lib.exceptions import HokusaiError

from test import HokusaiUnitTestCase

TMP_CONFIG_FILE = os.path.join(os.getcwd(), 'test', 'tmp', 'config.yml')

class TestConfig(HokusaiUnitTestCase):
  @classmethod
  def setUpClass(cls):
    cls.__hokusai_config_file = config.HOKUSAI_CONFIG_FILE
    config.HOKUSAI_CONFIG_FILE = TMP_CONFIG_FILE

  @classmethod
  def tearDownClass(cls):
    config.HOKUSAI_CONFIG_FILE = cls.__hokusai_config_file

  def setUp(self):
    self.config = config.config

  def test_requires_config(self):
    with self.assertRaises(HokusaiError):
      self.config.check()

  def test_create(self):
    self.assertFalse(os.path.isfile(TMP_CONFIG_FILE))
    try:
      self.config.create('foo', '123456789012', 'us-east-1')
      self.assertTrue(os.path.isfile(TMP_CONFIG_FILE))
      self.assertEqual(self.config.project_name, 'foo')
      self.assertEqual(self.config.aws_account_id, '123456789012')
      self.assertEqual(self.config.aws_ecr_region, 'us-east-1')
      self.assertEqual(self.config.aws_ecr_registry, '123456789012.dkr.ecr.us-east-1.amazonaws.com/foo')
    finally:
      os.remove(TMP_CONFIG_FILE)
