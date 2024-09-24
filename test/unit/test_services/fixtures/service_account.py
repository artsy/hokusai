import json
import pytest

@pytest.fixture
def mock_sa_spec():
  spec = {
    "apiVersion": "v1",
    "imagePullSecrets": [
      {
        "name": "foosecret"
      }
    ],
    "kind": "ServiceAccount",
    "metadata": {
      "annotations": {},
      "name": "foosa",
      "namespace": "default",
    }
  }
  return spec

@pytest.fixture
def mock_k8s_sa_json_string():
  sa_json = {
    "apiVersion": "v1",
    "imagePullSecrets": [
      {
        "name": "foosecret"
      }
    ],
    "kind": "ServiceAccount",
    "metadata": {
        "annotations": {
            "kubectl.kubernetes.io/last-applied-configuration": "blah"
        },
        "creationTimestamp": "2020-11-08T20:59:49Z",
        "name": "foosa",
        "namespace": "default",
        "resourceVersion": "123",
        "uid": "123-456"
    },
    "secrets": [
      {
        "name": "default-token-123"
      }
    ]
  }
  return json.dumps(sa_json)
