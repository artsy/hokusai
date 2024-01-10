import pytest

mock_namespaces_json = [
  {
    'metadata': {
      'name': 'namespace1'
    }
  },
  {
    'metadata': {
      'name': 'namespace2'
    }
  }
]

@pytest.fixture
def mock_kubectl_obj():
  class MockKubectl:
    def __init__(self):
      pass
    def get_objects(self, obj, selector=None):
      if obj == 'namespaces':
        return mock_namespaces_json
  return MockKubectl()
