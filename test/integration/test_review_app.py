import os
import httpretty
import sys
from unittest.mock import patch

from test import HokusaiIntegrationTestCase, TEST_KUBE_CONTEXT
from test.utils import captured_output
from test.mocks.mock_ecr import MockECR

from hokusai import CWD
from hokusai.lib.common import shout
from hokusai.commands import kubernetes
from hokusai.commands.namespace import create_new_app_yaml
from hokusai.lib.common import shout
from hokusai.services.kubectl import Kubectl

class TestReviewApp(HokusaiIntegrationTestCase):
    @classmethod
    def setUpClass(cls):
        kubernetes.ECR = MockECR
        kubernetes.HOKUSAI_CONFIG_DIR = os.path.join(CWD, 'test/fixtures/project/hokusai')
        cls.kubernetes_yml = os.path.abspath(os.path.join(kubernetes.HOKUSAI_CONFIG_DIR, 'a-review-app.yml'))
        cls.kctl = Kubectl(TEST_KUBE_CONTEXT)

    @classmethod
    def tearDownClass(cls):
        with captured_output() as (out, err):
            shout(cls.kctl.command("delete ns a-review-app"), print_output=True)

    @httpretty.activate
    @patch('hokusai.lib.command.sys.exit')
    def test_create_review_app_yaml_file(self, mocked_sys_exit):
        httpretty.register_uri(httpretty.POST, "https://sts.amazonaws.com/",
                                body=self.fixture('sts-get-caller-identity-response.xml'),
                                content_type="application/xml")
        httpretty.register_uri(httpretty.POST, "https://api.ecr.us-east-1.amazonaws.com/",
                                body=self.fixture('ecr-repositories-response.json'),
                                content_type="application/x-amz-json-1.1")

        review_app_yaml_file = os.path.join(CWD, 'hokusai', 'a-review-app.yml')
        try:
            create_new_app_yaml(os.path.abspath(os.path.join(CWD, 'test/fixtures/project/hokusai/minikube.yml')), 'a-review-app')
            self.assertTrue(os.path.isfile(review_app_yaml_file))
        finally:
            os.remove(review_app_yaml_file)

    @httpretty.activate
    @patch('hokusai.lib.command.sys.exit')
    def test_01_k8s_create(self, mocked_sys_exit):
        httpretty.register_uri(httpretty.POST, "https://sts.amazonaws.com/",
                            body=self.fixture('sts-get-caller-identity-response.xml'),
                            content_type="application/xml")
        httpretty.register_uri(httpretty.POST, "https://api.ecr.us-east-1.amazonaws.com/",
                                body=self.fixture('ecr-repositories-response.json'),
                                content_type="application/x-amz-json-1.1")

        review_app_yaml_file = os.path.join(CWD, 'hokusai', 'a-review-app.yml')
        with captured_output() as (out, err):
          try:
            create_new_app_yaml(os.path.abspath(os.path.join(CWD, 'test/fixtures/project/hokusai/minikube.yml')), 'a-review-app')
            mocked_sys_exit.assert_called_once_with(0)
            mocked_sys_exit.reset_mock()
            kubernetes.k8s_create(TEST_KUBE_CONTEXT, filename=review_app_yaml_file)
            mocked_sys_exit.assert_called_once_with(0)
            namespaces = shout(self.kctl.command("get ns -l app-phase=review"))
            self.assertIn("a-review-app", namespaces)
            self.assertNotIn("default", namespaces)
          finally:
            os.remove(review_app_yaml_file)
