import os

from hokusai.lib import config
from hokusai.lib.exceptions import HokusaiError

from test import HokusaiUnitTestCase

TMP_CONFIG_FILE = os.path.join('/tmp', 'config.yml')

class TestConfigSetup(HokusaiUnitTestCase):
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
      self.config.create('bar')
      self.assertTrue(os.path.isfile(TMP_CONFIG_FILE))
      self.assertEqual(self.config.project_name, 'bar')
    finally:
      os.remove(TMP_CONFIG_FILE)

class TestConfig(HokusaiUnitTestCase):
  def test_config_from_file(self):
    self.assertEqual(config.config.project_name, 'foo')
    self.assertEqual(config.config.pre_deploy, 'migrate.sh')
    self.assertEqual(config.config.post_deploy, 'sh -c report.sh')
    self.assertEqual(config.config.git_remote, 'git@github.com:artsy/hokusai.git')

  def test_config_from_environment(self):
    self.assertEqual(config.config.run_tty, False)
    os.environ['HOKUSAI_RUN_TTY'] = 'True'
    self.assertEqual(config.config.run_tty, True)
