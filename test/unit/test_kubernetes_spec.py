import os

import yaml

from test import HokusaiUnitTestCase

from hokusai import CWD
from hokusai.lib.exceptions import HokusaiError

from hokusai.services.kubernetes_spec import KubernetesSpec

class TestKubernetesSpec(HokusaiUnitTestCase):
  def setUp(self):
    self.kubernetes_yml = os.path.join(CWD, 'test/fixtures/kubernetes-config.yml')

  def test_kubernetes_spec(self):
    kubernetes_spec = KubernetesSpec(self.kubernetes_yml).to_list()
    self.assertEqual(kubernetes_spec[0]['spec']['template']['spec']['containers'][0]['image'], 'eggs')
