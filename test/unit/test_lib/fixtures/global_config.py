import pytest


def load_for_spy(uri):
  return {
    'kubectl-version': 'foo',
    'kubeconfig-dir': 'foo',
    'kubeconfig-source-uri': 'foo',
    'kubectl-dir': 'foo'
  }

@pytest.fixture
def mock_config_loader_class():
  class ConfigLoader():
    def __init__(self, uri):
      self._uri = uri
    def load(self):
      return load_for_spy(self._uri)
  return ConfigLoader
