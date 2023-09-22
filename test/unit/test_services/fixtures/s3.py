import pytest

@pytest.fixture
def mock_s3_client():
  class MockS3Client:
    def download_file(self, bucket_name, key_name, target_file):
      pass
  return MockS3Client()
