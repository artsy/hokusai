import pytest


def download_for_spy(uri, path):
  pass

@pytest.fixture
def mock_local_to_local_raise():
  def mock_local_to_local():
    raise Exception
  return mock_local_to_local

@pytest.fixture
def mock_s3_interface_class():
  class MockS3Interface:
    def download(self, uri, path):
      download_for_spy(uri, path)
  return MockS3Interface
