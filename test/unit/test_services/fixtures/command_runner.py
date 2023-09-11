import pytest

@pytest.fixture
def mock_spec():
  return {
    'apiVersion': 'v1',
    'spec': {
      'containers': [
        {
          'args': ['foocmd'],
          'name': 'hello-hokusai-run-jxu-abcde',
          'image': 'foo:footag',
          'imagePullPolicy': 'Always',
          'env': [{'name': 'foo', 'value': 'bar'}],
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
      ],
      'nodeSelector': {'fooconstraint': 'bar'}
    }
  }

@pytest.fixture
def mock_tty_spec():
  return {
    'apiVersion': 'v1',
    'spec': {
      'containers': [
        {
          'args': ['foocmd'],
          'name': 'hello-hokusai-run-jxu-abcde',
          'image': 'foo:footag',
          'imagePullPolicy': 'Always',
          'env': [{'name': 'foo', 'value': 'bar'}],
          'envFrom': [
              {
                'configMapRef': {'name': 'hello-environment'}
              },
              {
                'secretRef': {'name': 'hello', 'optional': True}
              }
          ],
          "stdin": True,
          "stdinOnce": True,
          "tty": True
        }
      ],
      'nodeSelector': {'fooconstraint': 'bar'}
    }
  }
