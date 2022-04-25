from click.testing import CliRunner
from hokusai.cli.base import base
from test import HokusaiSmokeTestCase

class TestReviewApp(HokusaiSmokeTestCase):
  def test_review_app_with_underscore(self):
    runner = CliRunner()
    result = runner.invoke(base, ['review_app'])
    assert result.exit_code == 0
  def test_review_app_with_dash(self):
    runner = CliRunner()
    result = runner.invoke(base, ['review-app'])
    assert result.exit_code != 0
