import pytest

@pytest.fixture
def test_k8s_spec_as_string():
  return "---\napiVersion: extensions/v1beta1\nkind: Deployment\nmetadata:\n  name: {{ project_name }}\n  namespace: default\nspec:\n  strategy:\n    rollingUpdate:\n      maxSurge: 1\n      maxUnavailable: 0\n    type: RollingUpdate\n  template:\n{% include 'deployment-metadata.yml' %}\n    spec:\n      containers:\n        {%- for container in vars.containers %}\n        - name: {{ container.name }}\n          image: {{ vars.imageTag }}\n        {%- endfor %}"
