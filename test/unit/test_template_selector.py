import os

import yaml

from test import HokusaiUnitTestCase

from hokusai import CWD
from hokusai.lib.exceptions import HokusaiError

from hokusai.lib.template_selector import TemplateSelector

class TestTemplateSelector(HokusaiUnitTestCase):
  def setUp(self):
    self.template_path = os.path.join(CWD, 'test/fixtures/project/hokusai')

  def test_finds_yml_file(self):
    test_file = os.path.join(self.template_path, 'test.yml')
    open(test_file, 'a').close()
    self.assertEqual(TemplateSelector().get(os.path.join(self.template_path, 'test')), test_file)
    os.remove(test_file)

  def test_finds_yaml_file(self):
    test_file = os.path.join(self.template_path, 'test.yaml')
    open(test_file, 'a').close()
    self.assertEqual(TemplateSelector().get(os.path.join(self.template_path, 'test')), test_file)
    os.remove(test_file)

  def test_finds_yml_j2_file(self):
    test_file = os.path.join(self.template_path, 'test.yml.j2')
    open(test_file, 'a').close()
    self.assertEqual(TemplateSelector().get(os.path.join(self.template_path, 'test')), test_file)
    os.remove(test_file)

  def test_finds_yaml_j2_file(self):
    test_file = os.path.join(self.template_path, 'test.yaml.j2')
    open(test_file, 'a').close()
    self.assertEqual(TemplateSelector().get(os.path.join(self.template_path, 'test')), test_file)
    os.remove(test_file)

  def test_finds_explicit_file_or_errors(self):
    with self.assertRaises(HokusaiError):
      TemplateSelector().get(os.path.join(self.template_path, 'test.yml'))
    test_file = os.path.join(self.template_path, 'test.yml')
    open(test_file, 'a').close()
    self.assertEqual(TemplateSelector().get(os.path.join(self.template_path, 'test.yml')), test_file)
    os.remove(test_file)

  def test_errors_with_no_template_found(self):
    with self.assertRaises(HokusaiError):
      TemplateSelector().get(os.path.join(self.template_path, 'test'))
