import os

import yaml

from test import HokusaiUnitTestCase

from hokusai import CWD
from hokusai.lib.exceptions import HokusaiError

from hokusai.lib.template_renderer import TemplateRenderer

class TestTemplateRenderer(HokusaiUnitTestCase):
  def setUp(self):
    self.template_path = os.path.join(CWD, 'test/fixtures/kubernetes-config.yml')

  def test_template_renderer_renders_vars(self):
    template_config = {
      'vars': {
        'containers': [{'name': 'project-name-web'}],
        'imageTag': 'spam'
        }
    }
    template_renderer = TemplateRenderer(self.template_path, template_config)
    k8s_payload = list(yaml.safe_load_all(template_renderer.render()))
    self.assertEqual(k8s_payload[0]['spec']['template']['spec']['containers'][0]['name'], 'project-name-web')
    self.assertEqual(k8s_payload[0]['spec']['template']['spec']['containers'][0]['image'], 'spam')

  def test_template_renderer_errors_on_missing_variables(self):
    template_config = { }
    template_renderer = TemplateRenderer(self.template_path, template_config)
    with self.assertRaises(HokusaiError):
      template_renderer.render()
