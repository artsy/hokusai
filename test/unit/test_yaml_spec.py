import os

import httpretty

from test import HokusaiUnitTestCase

from hokusai import CWD
from hokusai.lib.exceptions import HokusaiError

from hokusai.services.yaml_spec import YamlSpec

httpretty.enable()
httpretty.HTTPretty.allow_net_connect = False

class TestYamlSpec(HokusaiUnitTestCase):
  def setUp(self):
    self.kubernetes_yml = os.path.join(CWD, 'test/fixtures/kubernetes-config.yml')

  @httpretty.activate
  def test_yaml_spec(self):
    httpretty.register_uri(httpretty.POST, "https://sts.amazonaws.com/",
                            body=self.fixture('sts-get-caller-identity-response.xml'),
                            content_type="application/xml")
    httpretty.register_uri(httpretty.POST, "https://api.ecr.us-east-1.amazonaws.com/",
                            body=self.fixture('ecr-repositories-response.json'),
                            content_type="application/x-amz-json-1.1")
    yaml_spec = YamlSpec(self.kubernetes_yml).to_list()
    self.assertEqual(yaml_spec[0]['metadata']['name'], 'hello')
    self.assertEqual(yaml_spec[0]['spec']['template']['spec']['containers'][0]['name'], 'web')
    self.assertEqual(yaml_spec[0]['spec']['template']['spec']['containers'][0]['image'], 'eggs')
    self.assertEqual(yaml_spec[0]['spec']['template']['spec']['containers'][1]['name'], 'worker')
    self.assertEqual(yaml_spec[0]['spec']['template']['spec']['containers'][1]['image'], 'eggs')
