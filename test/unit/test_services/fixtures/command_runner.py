import pytest

@pytest.fixture
def mock_overrides_spec():
  return {
    'apiVersion': 'v1',
    'spec': {
      'containers': [
        {
          'args': ['sh', '-c', 'source /path/to/secrets/file && foocmd'],
          'name': 'hello-hokusai-run-foouser-abcde',
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
          'name': 'hello-hokusai-run-foouser-abcde',
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

@pytest.fixture
def mock_ecr_class():
  class mock_ECR:
    def __init__(self):
      pass
  return mock_ECR

@pytest.fixture
def mock_clean_pod_spec():
  return {
    'containers': [
      {
        'args': ['foocmd'],
        'name': 'hello-hokusai-run-foouser-abcde',
        'image': 'foo:footag',
        'imagePullPolicy': 'Always',
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
    ]
  }

@pytest.fixture
def mock_pod_spec():
  return {
    'containers': [
      {
        'args': ['foocmd'],
        'name': 'hello-hokusai-run-foouser-abcde',
        'image': 'foo:footag',
        'imagePullPolicy': 'Always',
        'ports': [
          {
            'name': 'foo-http',
            'containerPort': '8080'
          }
        ],
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

@pytest.fixture
def mock_clean_containers_spec():
  return [
    {
      'args': ['foocmd'],
      'name': 'hello-hokusai-run-foouser-abcde',
      'image': 'foo:footag',
      'imagePullPolicy': 'Always',
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
  ]
