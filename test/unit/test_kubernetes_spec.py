import os

import httpretty

from test import HokusaiUnitTestCase

from hokusai import CWD
from hokusai.lib.exceptions import HokusaiError

from hokusai.services.kubernetes_spec import KubernetesSpec

httpretty.enable()
httpretty.HTTPretty.allow_net_connect = False

class TestKubernetesSpec(HokusaiUnitTestCase):
  def setUp(self):
    self.kubernetes_yml = os.path.join(CWD, 'test/fixtures/kubernetes-config.yml')

  @httpretty.activate
  def test_kubernetes_spec(self):
    httpretty.register_uri(httpretty.POST, "https://sts.amazonaws.com/",
                            body=open(os.path.join(os.getcwd(), 'test', 'fixtures', 'sts-get-caller-identity-response.xml')).read(),
                            content_type="application/xml")
    httpretty.register_uri(httpretty.POST, "https://api.ecr.us-east-1.amazonaws.com/",
                            body=open(os.path.join(os.getcwd(), 'test', 'fixtures', 'ecr-repositories-response.json')).read(),
                            content_type="application/x-amz-json-1.1")
    kubernetes_spec = KubernetesSpec(self.kubernetes_yml).to_list()
    self.assertEqual(kubernetes_spec[0]['spec']['template']['spec']['containers'][0]['image'], 'eggs')
