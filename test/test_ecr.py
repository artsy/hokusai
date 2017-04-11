import os

import httpretty

from test import HokusaiUnitTestCase
from hokusai.ecr import ECR

httpretty.enable()
httpretty.HTTPretty.allow_net_connect = False

class TestECR(HokusaiUnitTestCase):
  def setUp(self):
    self.ecr = ECR()

  @httpretty.activate
  def test_get_login(self):
    httpretty.register_uri(httpretty.POST, "https://ecr.us-east-1.amazonaws.com/",
                           body='{"authorizationData":[{"authorizationToken":"QVdTOjc2VzhZRVVGSERTQUU5OERGREhTRlNERklVSFNEQUpLR0tTQURGR0tERg==","expiresAt":1E9,"proxyEndpoint":"https://12345.dkr.ecr.us-east-1.amazonaws.com"}]}',
                           content_type="application/x-amz-json-1.1")
    self.assertEqual(self.ecr.get_login(), 'docker login -u AWS -p 76W8YEUFHDSAE98DFDHSFSDFIUHSDAJKGKSADFGKDF -e none https://12345.dkr.ecr.us-east-1.amazonaws.com')
