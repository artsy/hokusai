import pytest

@pytest.fixture
def expected_default_configmap_struct():
  return {
    'apiVersion': 'v1',
    'kind': 'ConfigMap',
    'metadata': {
      'name': 'hello-environment',
      'namespace': 'default',
      'labels': {
        'app': 'hello'
      }
    },
    'data': {}
  }
