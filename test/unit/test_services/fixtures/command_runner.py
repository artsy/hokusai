import pytest

@pytest.fixture
def mock_spec():
  return {
    'args': ['foocmd'],
    'name': 'hello-hokusai-run-jxu-abcde',
    'image': 'foo:footag',
    'imagePullPolicy': 'Always',
    'env': [],
    'envFrom':
      [
        {
          'configMapRef': {'name': 'hello-environment'}
        },
        {
          'secretRef': {'name': 'hello', 'optional': True}
        }
      ]
  }
