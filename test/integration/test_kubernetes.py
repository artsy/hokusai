import os

from mock import patch

from test import HokusaiIntegrationTestCase, TEST_KUBE_CONTEXT
from test.utils import captured_output, mock_verbosity
from test.mocks.mock_ecr import MockECR

from hokusai import CWD
from hokusai.lib.common import shout
from hokusai.commands import kubernetes
from hokusai.services.kubectl import Kubectl

kubernetes.HOKUSAI_CONFIG_DIR = os.path.join(CWD, 'test/fixtures/project/hokusai')

class TestKubernetes(HokusaiIntegrationTestCase):
    def setUp(self):
        kubernetes.ECR = MockECR
    def tearDown(self):
        shout(Kubectl(TEST_KUBE_CONTEXT).command("delete all --selector testFixture=true"), print_output=True)

    @patch('hokusai.lib.command.sys.exit')
    def test_k8s_create(self, mocked_sys_exit):
        with mock_verbosity(True):
            # with captured_output() as (out, err):
            kubernetes.k8s_create(TEST_KUBE_CONTEXT, yaml_file_name='minikube')
            mocked_sys_exit.assert_called_once_with(0)

            kubernetes_yml = os.path.join(CWD, "%s/%s.yml" % (kubernetes.HOKUSAI_CONFIG_DIR, 'minikube'))
            shout(Kubectl(TEST_KUBE_CONTEXT).command("get -f %s" % kubernetes_yml), print_output=True)
