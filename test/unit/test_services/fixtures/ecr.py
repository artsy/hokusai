import pytest

@pytest.fixture
def mock_ecr_class():
  class mock_ECR:
    def __init__(self):
      self.project_repo = 'foo'
  return mock_ECR
