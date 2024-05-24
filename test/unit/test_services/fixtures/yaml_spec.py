import pytest

@pytest.fixture
def test_k8s_spec_as_string():
  test_k8s_spec = 'test/fixtures/kubernetes-config.yml'
  with open(test_k8s_spec, 'r') as f:
    content = f.read().strip()
  return content
