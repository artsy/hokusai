import pytest


@pytest.fixture
def mock_uri_to_local_raise():
  def mock_uri_to_local(a, b, c):
    raise Exception
  return mock_uri_to_local
