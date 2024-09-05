import pytest

@pytest.fixture
def mock_shout_raises():
  def mock_shout(cmd, print_output=False):
    raise ValueError
  return mock_shout

@pytest.fixture
def mock_kubectl_obj():
  class MockKubectl:
    def __init__(self):
      pass
    def create(self, file):
      pass
    def command(self, cmd):
      return 'the command'
    def apply(self, path):
      pass
  return MockKubectl()
