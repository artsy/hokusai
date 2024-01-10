import os
import httpretty
import sys
from unittest.mock import patch

from test import HokusaiIntegrationTestCase, TEST_KUBE_CONTEXT
from test.utils import captured_output, mock_verbosity
from test.mocks.mock_ecr import MockECR

from hokusai import CWD
from hokusai.lib.common import shout
from hokusai.commands import kubernetes
from hokusai.services.kubectl import Kubectl
from hokusai.services.deployment import Deployment
from hokusai.services.configmap import ConfigMap


class TestKubernetes(HokusaiIntegrationTestCase):
    @classmethod
    def setUpClass(cls):
        kubernetes.ECR = MockECR
        kubernetes.HOKUSAI_CONFIG_DIR = os.path.join(CWD, 'test/fixtures/project/hokusai')
        cls.kubernetes_yml = os.path.abspath(os.path.join(kubernetes.HOKUSAI_CONFIG_DIR, 'minikube.yml'))
        cls.kctl = Kubectl(TEST_KUBE_CONTEXT)

    @classmethod
    def tearDownClass(cls):
        with captured_output() as (out, err):
            shout(cls.kctl.command("delete all --selector testFixture=true"), print_output=True)

    @httpretty.activate
    def test_00_k8s_env_create(self):
        configmap = ConfigMap(TEST_KUBE_CONTEXT)
        configmap.create()


    @httpretty.activate
    def test_01_k8s_create(self):
        httpretty.register_uri(httpretty.POST, "https://sts.amazonaws.com/",
                            body=self.fixture('sts-get-caller-identity-response.xml'),
                            content_type="application/xml")
        httpretty.register_uri(httpretty.POST, "https://api.ecr.us-east-1.amazonaws.com/",
                                body=self.fixture('ecr-repositories-response.json'),
                                content_type="application/x-amz-json-1.1")
        with captured_output() as (out, err):
            kubernetes.k8s_create(TEST_KUBE_CONTEXT, filename=self.__class__.kubernetes_yml)
            self.assertIn('Created Kubernetes environment %s' % self.__class__.kubernetes_yml,
                            out.getvalue().strip())

        deployments = shout(self.kctl.command("get deployments"))
        self.assertIn("hello-web", deployments)

    @httpretty.activate
    def test_02_k8s_update(self):
        httpretty.register_uri(httpretty.POST, "https://sts.amazonaws.com/",
                            body=self.fixture('sts-get-caller-identity-response.xml'),
                            content_type="application/xml")
        httpretty.register_uri(httpretty.POST, "https://api.ecr.us-east-1.amazonaws.com/",
                                body=self.fixture('ecr-repositories-response.json'),
                                content_type="application/x-amz-json-1.1")
        with captured_output() as (out, err):
            kubernetes.k8s_update(TEST_KUBE_CONTEXT, filename=self.__class__.kubernetes_yml, skip_checks=True)
            # self.assertIn('deployment.apps "hello-web" unchanged', out.getvalue().strip())
            # self.assertIn('service "hello-web" unchanged', out.getvalue().strip())
            self.assertIn('Updated Kubernetes environment %s' % self.__class__.kubernetes_yml,
                            out.getvalue().strip())

    @httpretty.activate
    def test_03_k8s_status(self):
        httpretty.register_uri(httpretty.POST, "https://sts.amazonaws.com/",
                            body=self.fixture('sts-get-caller-identity-response.xml'),
                            content_type="application/xml")
        httpretty.register_uri(httpretty.POST, "https://api.ecr.us-east-1.amazonaws.com/",
                                body=self.fixture('ecr-repositories-response.json'),
                                content_type="application/x-amz-json-1.1")
        with captured_output() as (out, err):
            kubernetes.k8s_status(TEST_KUBE_CONTEXT, True, False, False, False, filename=self.__class__.kubernetes_yml)
            self.assertIn('Resources', out.getvalue().strip())
            # self.assertIn('deployment.apps/hello-web', out.getvalue().strip())
            # self.assertIn('service/hello-web', out.getvalue().strip())

            kubernetes.k8s_status(TEST_KUBE_CONTEXT, True, False, True, False, filename=self.__class__.kubernetes_yml)
            self.assertIn('Resources', out.getvalue().strip())
            # self.assertIn('Name:                   hello-web', out.getvalue().strip())
            # self.assertIn('Selector:               app=hello', out.getvalue().strip())

            kubernetes.k8s_status(TEST_KUBE_CONTEXT, False, True, False, False, filename=self.__class__.kubernetes_yml)
            self.assertIn('Pods', out.getvalue().strip())
            # self.assertIn('hello-web', out.getvalue().strip())
            # self.assertTrue('ContainerCreating' in out.getvalue().strip() or 'Running' in out.getvalue().strip())

            kubernetes.k8s_status(TEST_KUBE_CONTEXT, False, True, True, False, filename=self.__class__.kubernetes_yml)
            # self.assertIn('Name:           hello-web', out.getvalue().strip())

            # TODO enable heapster in minikube to get top pods
            # kubernetes.k8s_status(TEST_KUBE_CONTEXT, False, False, False, True, filename=self.__class__.kubernetes_yml)


    @httpretty.activate
    def test_04_deployment_refresh(self):
        deployment = Deployment(TEST_KUBE_CONTEXT)
        deployment.refresh()


    @httpretty.activate
    def test_05_k8s_delete(self):
        httpretty.register_uri(httpretty.POST, "https://sts.amazonaws.com/",
                            body=self.fixture('sts-get-caller-identity-response.xml'),
                            content_type="application/xml")
        httpretty.register_uri(httpretty.POST, "https://api.ecr.us-east-1.amazonaws.com/",
                                body=self.fixture('ecr-repositories-response.json'),
                                content_type="application/x-amz-json-1.1")
        with captured_output() as (out, err):
            kubernetes.k8s_delete(TEST_KUBE_CONTEXT, filename=self.__class__.kubernetes_yml)
            self.assertIn('Deleted Kubernetes environment %s' % self.__class__.kubernetes_yml,
                            out.getvalue().strip())

    @httpretty.activate
    def test_06_k8s_env_destroy(self):
        configmap = ConfigMap(TEST_KUBE_CONTEXT)
        configmap.destroy()
