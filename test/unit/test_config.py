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
    self.assertFalse(self.config._check_config_present(TMP_CONFIG_FILE))

  def test_create(self):
    self.assertFalse(os.path.isfile(TMP_CONFIG_FILE))
    try:
      self.config.create('bar')
      self.assertTrue(os.path.isfile(TMP_CONFIG_FILE))
      self.assertTrue(self.config._check_config_present(TMP_CONFIG_FILE))
      self.assertEqual(self.config.project_name, 'bar')
    finally:
      os.remove(TMP_CONFIG_FILE)

  def test_check_hokusai_required_version(self):
    self.assertTrue(self.config._check_required_version(None, '0.0.1'))
    with self.assertRaises(HokusaiError):
      self.config._check_required_version('0.0.1', '0.0.1')
    with self.assertRaises(HokusaiError):
      self.config._check_required_version('someinvalidversionspecifier', '0.0.1')
    self.assertTrue(self.config._check_required_version('~=0.1', '0.1.1'))
    self.assertTrue(self.config._check_required_version('~=0.1', '0.2'))
    self.assertFalse(self.config._check_required_version('~=0.1', '1.0'))
    self.assertTrue(self.config._check_required_version('==0.0.1', '0.0.1'))
    self.assertFalse(self.config._check_required_version('==0.0.1', '0.0.2'))
    self.assertFalse(self.config._check_required_version('==1.0', '0.2'))
    self.assertTrue(self.config._check_required_version('<0.0.2.post2', '0.0.2.post1'))
    self.assertTrue(self.config._check_required_version('<1.1', '1.0.2'))
    self.assertFalse(self.config._check_required_version('<1.1', '2.0.2'))
    self.assertFalse(self.config._check_required_version('<=0.0.2', '2.2'))
    self.assertTrue(self.config._check_required_version('<=2.2', '2.2'))
    self.assertTrue(self.config._check_required_version('>0.0.1', '1.2.3'))
    self.assertTrue(self.config._check_required_version('>0.0.1.post1', '0.0.1.post3'))
    self.assertTrue(self.config._check_required_version('>=0.0.1', '1.2.3'))
    self.assertTrue(self.config._check_required_version('>=1.2.3', '1.2.3'))
    self.assertTrue(self.config._check_required_version('!=0.0.1', '1.2.3'))
    self.assertFalse(self.config._check_required_version('!=0.0.1', '0.0.1'))
    self.assertFalse(self.config._check_required_version('!=0.1.*', '0.1.1'))
    self.assertTrue(self.config._check_required_version('===1.0+trololo', '1.0+trololo'))
    self.assertFalse(self.config._check_required_version('===1.0+trololo', '1.0+tralala'))
    self.assertTrue(self.config._check_required_version('>0.0.1,~=0.2,!=0.2.3', '0.2.2'))
    self.assertFalse(self.config._check_required_version('>0.0.1,~=0.2,!=0.2.3', '0.2.3'))
    self.assertTrue(self.config._check_required_version('>0.1', '0.2b1'))
    self.assertFalse(self.config._check_required_version('>0.2', '0.2b1'))

class TestConfig(HokusaiUnitTestCase):
  def test_config_from_file(self):
    self.assertEqual(config.config.project_name, 'hello')
    self.assertEqual(config.config.pre_deploy, 'migrate.sh')
    self.assertEqual(config.config.post_deploy, 'sh -c report.sh')
    self.assertEqual(config.config.git_remote, 'git@github.com:artsy/hokusai.git')
    self.assertEqual(config.config.template_config_files, ['./test/fixtures/template_config.yml'])

  def test_config_from_environment(self):
    self.assertEqual(config.config.run_tty, False)
    os.environ['HOKUSAI_RUN_TTY'] = 'True'
    self.assertEqual(config.config.run_tty, True)
