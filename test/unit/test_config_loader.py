import os

from test import HokusaiUnitTestCase

from hokusai import CWD

from hokusai.lib.config_loader import ConfigLoader
from hokusai.lib.exceptions import HokusaiError

class TestConfigLoader(HokusaiUnitTestCase):
  def test_load_config(self):
    _config_file = os.path.join(CWD, 'test/fixtures/template_config.yml')
    config_loader = ConfigLoader(_config_file)
    template_config = config_loader.load()
    self.assertEqual("eggs", template_config["vars"]["imageTag"])
