import pytest

@pytest.fixture
def expected_namespace_struct():
  return {
    'apiVersion': 'v1',
    'kind': 'Namespace',
    'metadata': {
      'name': 'foons',
      'labels': {}
    }
  }
