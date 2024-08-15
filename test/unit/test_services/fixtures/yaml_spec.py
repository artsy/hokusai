import pytest

@pytest.fixture
def test_k8s_spec_as_string():
  return "---\napiVersion: extensions/v1beta1\nkind: Deployment\nmetadata:\n  name: {{ project_name }}\n  namespace: default\nspec:\n  strategy:\n    rollingUpdate:\n      maxSurge: 1\n      maxUnavailable: 0\n    type: RollingUpdate\n  template:\n{% include 'deployment-metadata.yml' %}\n    spec:\n      containers:\n        {%- for container in vars.containers %}\n        - name: {{ container.name }}\n          image: {{ vars.imageTag }}\n        {%- endfor %}"

@pytest.fixture
def mock_hokusai_yaml():
  return [
    {
      'apiVersion': 'apps/v1',
      'kind': 'Deployment',
      'metadata': {
        'name': 'foo-deployment1'
      },
      'spec': {
        'template': {
          'spec': {
            'containers': ['foo-deployment1-container']
          }
        }
      }
    },
    {
      'apiVersion': 'apps/v1',
      'kind': 'Deployment',
      'metadata': {
        'name': 'foo-deployment2'
      },
      'spec': {
        'template': {
          'spec': {
            'containers': ['foo-deployment2-container']
          }
        }
      }
    },
    {
      'apiVersion': 'apps/v1',
      'kind': 'Service',
      'metadata': {
        'name': 'foo-service'
      }
    }
  ]

@pytest.fixture
def mock_hokusai_yaml_deployment():
  return [
    {
      'apiVersion': 'apps/v1',
      'kind': 'Deployment',
      'metadata': {
        'name': 'foo-deployment1'
      },
      'spec': {
        'template': {
          'spec': {
            'containers': ['foo-deployment1-container']
          }
        }
      }
    },
    {
      'apiVersion': 'apps/v1',
      'kind': 'Deployment',
      'metadata': {
        'name': 'foo-deployment2'
      },
      'spec': {
        'template': {
          'spec': {
            'containers': ['foo-deployment2-container']
          }
        }
      }
    }
  ]

@pytest.fixture
def mock_hokusai_yaml_deployment_one():
  return {
    'apiVersion': 'apps/v1',
    'kind': 'Deployment',
    'metadata': {
      'name': 'foo-deployment1'
    },
    'spec': {
      'template': {
        'spec': {
          'containers': ['foo-deployment1-container']
        }
      }
    }
  }

@pytest.fixture
def mock_hokusai_yaml_deployment_one_bad():
  return {
    'apiVersion': 'apps/v1',
    'kind': 'Deployment',
    'metadata': {
      'name': 'foo-deployment1'
    },
    'spec': {
      'template': {
        'spec': {}
      }
    }
  }
