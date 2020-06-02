import os

from test import HokusaiUnitTestCase

import httpretty

import yaml

from hokusai import CWD

from hokusai.lib import docker_compose_helpers

httpretty.enable()
httpretty.HTTPretty.allow_net_connect = False

class TestDockerComposeHelpers(HokusaiUnitTestCase):
  def setUp(self):
    docker_compose_helpers.HOKUSAI_CONFIG_DIR = os.path.join(CWD, 'test/fixtures/project/hokusai')

  def tearDown(self):
    docker_compose_helpers.HOKUSAI_CONFIG_DIR = 'hokusai'

  @httpretty.activate
  def test_follows_extends(self):
    httpretty.register_uri(httpretty.POST, "https://sts.amazonaws.com/",
                            body=open(os.path.join(os.getcwd(), 'test', 'fixtures', 'sts-get-caller-identity-response.xml')).read(),
                            content_type="application/xml")
    httpretty.register_uri(httpretty.POST, "https://api.ecr.us-east-1.amazonaws.com/",
                            body=open(os.path.join(os.getcwd(), 'test', 'fixtures', 'ecr-repositories-response.json')).read(),
                            content_type="application/x-amz-json-1.1")
    docker_compose_yml = os.path.join(CWD, 'test/fixtures/project/hokusai/docker-compose-extends.yml')
    rendered_templates = docker_compose_helpers.follow_extends(docker_compose_yml)
    self.assertEqual(len(rendered_templates), 1)

    with open(rendered_templates[0], 'r') as f:
      struct = yaml.safe_load(f.read())
      self.assertEqual(struct['services']['nancy']['build']['context'], '../')
