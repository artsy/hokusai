import pytest

@pytest.fixture
def mock_global_config():
  class MockGlobalConfig():
    def __init__(self, uri='foouri'):
      self.kubeconfig_source_uri = 'fookubeconfiguri',
      self.kubeconfig_dir = 'fookubeconfigdir'
      self.kubectl_version = 'fookubectlversion'
      self.kubectl_dir = 'fookubectldir'
    def merge(self, **kwargs):
      pass
    def save(self):
      pass
  return MockGlobalConfig

@pytest.fixture
def mock_urlretrieve_raise():
  def mock_urlretrieve(a, b):
    raise Exception
  return mock_urlretrieve
