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
            'initContainers': [
              {
                'name': 'foo-deployment1-init-container',
                'envFrom': [
                  {
                    'configMapRef': {
                      'name': 'foo-deployment1-init-container-configmap'
                    }
                  }
                ]
              }
            ],
            'containers': [
              {
                'name': 'foo-deployment1-container',
                'envFrom': [
                  {
                    'configMapRef': {
                      'name': 'foo-deployment1-configmap1'
                    },
                  },
                  {
                    'configMapRef': {
                      'name': 'foo-deployment1-configmap2'
                    },
                  },
                  {
                    'someOtherRef': {
                      'name': 'foo-deployment1-blah'
                    }
                  }
                ]
              },
              {
                'name': 'foo-deployment1-container2',
                'envFrom': [
                  {
                    'configMapRef': {
                      'name': 'foo-deployment1-container2-configmap'
                    },
                  }
                ]
              }
            ],
            'serviceAccountName': 'foo-deployment1-sa'
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
            'containers': [
              {
                'name': 'foo-deployment2-container',
                'envFrom': [
                  {
                    'configMapRef': {
                      'name': 'foo-deployment2-configmap'
                    },
                  }
                ]
              }
            ],
            'serviceAccountName': 'foo-deployment2-sa'
          }
        }
      }
    },
    {
      'apiVersion': 'apps/v1',
      'kind': 'Deployment',
      'metadata': {
        'name': 'foo-deployment3'
      },
      'spec': {
        'template': {
          'spec': {
            'containers': [
              {
                'name': 'foo-deployment3-container',
                'envFrom': []
              }
            ]
          }
        }
      }
    },
    {
      'apiVersion': 'apps/v1',
      'kind': 'Deployment',
      'metadata': {
        'name': 'foo-deployment4'
      },
      'spec': {
        'template': {
          'spec': {
            'containers': [
              {
                'name': 'foo-deployment4-container'
              }
            ]
          }
        }
      }
    },
    {
      'apiVersion': 'apps/v1',
      'kind': 'Deployment',
      'metadata': {
        'name': 'foo-deployment5'
      },
      'spec': {
        'template': {
          'spec': {}
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
