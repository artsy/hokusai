import pytest

@pytest.fixture
def mock_shout_raises():
  def mock_shout(cmd, print_output=False):
    raise ValueError
  return mock_shout
