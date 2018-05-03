import os

import httpretty

from test import HokusaiIntegrationTestCase
from hokusai.services.ecr import ECR

httpretty.enable()
httpretty.HTTPretty.allow_net_connect = False

class TestECR(HokusaiIntegrationTestCase):
  def setUp(self):
    self.ecr = ECR()

  @httpretty.activate
  def test_registry(self):
    httpretty.register_uri(httpretty.POST, "https://sts.amazonaws.com/",
                            body=open(os.path.join(os.getcwd(), 'test', 'fixtures', 'sts-get-caller-identity-response.xml')).read(),
                            content_type="application/xml")
    httpretty.register_uri(httpretty.POST, "https://ecr.us-east-1.amazonaws.com/",
                            body=open(os.path.join(os.getcwd(), 'test', 'fixtures', 'ecr-repositories-response.json')).read(),
                            content_type="application/x-amz-json-1.1")
    repositories = [str(repo['repositoryName']) for repo in self.ecr.registry]
    self.assertTrue('foo' in repositories)
    self.assertTrue('bar' in repositories)
    self.assertTrue('baz' in repositories)

  @httpretty.activate
  def test_project_repo_exists(self):
    httpretty.register_uri(httpretty.POST, "https://sts.amazonaws.com/",
                            body=open(os.path.join(os.getcwd(), 'test', 'fixtures', 'sts-get-caller-identity-response.xml')).read(),
                            content_type="application/xml")
    httpretty.register_uri(httpretty.POST, "https://ecr.us-east-1.amazonaws.com/",
                            body=open(os.path.join(os.getcwd(), 'test', 'fixtures', 'ecr-repositories-response.json')).read(),
                            content_type="application/x-amz-json-1.1")
    self.assertTrue(self.ecr.project_repo_exists())

  @httpretty.activate
  def test_get_project_repo(self):
    httpretty.register_uri(httpretty.POST, "https://sts.amazonaws.com/",
                            body=open(os.path.join(os.getcwd(), 'test', 'fixtures', 'sts-get-caller-identity-response.xml')).read(),
                            content_type="application/xml")
    httpretty.register_uri(httpretty.POST, "https://ecr.us-east-1.amazonaws.com/",
                            body=open(os.path.join(os.getcwd(), 'test', 'fixtures', 'ecr-repositories-response.json')).read(),
                            content_type="application/x-amz-json-1.1")
    self.assertEqual(self.ecr.project_repo, '123456789012.dkr.ecr.us-east-1.amazonaws.com/foo')

  @httpretty.activate
  def test_create_project_repo(self):
    httpretty.register_uri(httpretty.POST, "https://sts.amazonaws.com/",
                            body=open(os.path.join(os.getcwd(), 'test', 'fixtures', 'sts-get-caller-identity-response.xml')).read(),
                            content_type="application/xml")
    httpretty.register_uri(httpretty.POST, "https://ecr.us-east-1.amazonaws.com/",
                            body=open(os.path.join(os.getcwd(), 'test', 'fixtures', 'ecr-create-repository-response.json')).read(),
                            content_type="application/x-amz-json-1.1")
    httpretty.register_uri(httpretty.POST, "https://ecr.us-east-1.amazonaws.com/",
                            body=open(os.path.join(os.getcwd(), 'test', 'fixtures', 'ecr-empty-repositories-response.json')).read(),
                            content_type="application/x-amz-json-1.1")
    self.assertTrue(self.ecr.create_project_repo())

  @httpretty.activate
  def test_get_login(self):
    httpretty.register_uri(httpretty.POST, "https://sts.amazonaws.com/",
                            body=open(os.path.join(os.getcwd(), 'test', 'fixtures', 'sts-get-caller-identity-response.xml')).read(),
                            content_type="application/xml")
    httpretty.register_uri(httpretty.POST, "https://ecr.us-east-1.amazonaws.com/",
                           body=open(os.path.join(os.getcwd(), 'test', 'fixtures', 'ecr-authorization-response.json')).read(),
                           content_type="application/x-amz-json-1.1")
    self.assertEqual(self.ecr.get_login(), 'docker login -u AWS -p 76W8YEUFHDSAE98DFDHSFSDFIUHSDAJKGKSADFGKDF https://123456789012.dkr.ecr.us-east-1.amazonaws.com')

  @httpretty.activate
  def test_get_images(self):
    httpretty.register_uri(httpretty.POST, "https://sts.amazonaws.com/",
                            body=open(os.path.join(os.getcwd(), 'test', 'fixtures', 'sts-get-caller-identity-response.xml')).read(),
                            content_type="application/xml")
    httpretty.register_uri(httpretty.POST, "https://ecr.us-east-1.amazonaws.com/",
                           body=open(os.path.join(os.getcwd(), 'test', 'fixtures', 'ecr-images-response.json')).read(),
                           content_type="application/x-amz-json-1.1")
    self.assertEqual(self.ecr.get_images()[0]['imageTags'], ['7shdn4f0f34bb8shdkb313cbeccb2fc031808duho', 'latest'])
    self.assertEqual(self.ecr.get_images()[0]['imageDigest'], 'sha256:8sh968hsn205e8bff53ba8ed1006c7f41dacd17db164efdn6d346204f997shdn')
    self.assertEqual(self.ecr.get_images()[0]['registryId'], '123456789012')
    self.assertEqual(self.ecr.get_images()[0]['repositoryName'], 'foo')

  @httpretty.activate
  def test_tag_exists(self):
    httpretty.register_uri(httpretty.POST, "https://sts.amazonaws.com/",
                            body=open(os.path.join(os.getcwd(), 'test', 'fixtures', 'sts-get-caller-identity-response.xml')).read(),
                            content_type="application/xml")
    httpretty.register_uri(httpretty.POST, "https://ecr.us-east-1.amazonaws.com/",
                           body=open(os.path.join(os.getcwd(), 'test', 'fixtures', 'ecr-images-response.json')).read(),
                           content_type="application/x-amz-json-1.1")
    self.assertTrue(self.ecr.tag_exists('7shdn4f0f34bb8shdkb313cbeccb2fc031808duho'))
    self.assertTrue(self.ecr.tag_exists('latest'))
