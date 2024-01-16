import os
import subprocess

import git
import pytest


TEST_GIT_REPO_NAME = 'hokusai-sandbox'

# this function is called before any test runs
def pytest_configure(config):
  # sanity check that 'staging' and 'production' kubernetes contexts point to minikube,
  # not to real Staging and Production clusters.
  resp = subprocess.run(
    'kubectl --context staging cluster-info',
    capture_output=True,
    shell=True,
    text=True,
    timeout=5
  )
  if not 'https://127.0.0.1:' in resp.stdout:
    msg = 'Error: Staging Kubernetes context does not point to 127.0.0.1. Is staging Minikube setup?'
    pytest.exit(msg)

  resp = subprocess.run(
    'kubectl --context production cluster-info',
    capture_output=True,
    shell=True,
    text=True,
    timeout=5
  )
  if not 'https://127.0.0.1:' in resp.stdout:
    msg = 'Error: Production Kubernetes context does not point to 127.0.0.1. Is production Minikube setup?'
    pytest.exit(msg)

  # clone test git repo
  os.chdir('test/integration/fixtures')
  # avoid cloning repeatedly when on local
  if not os.path.isdir(TEST_GIT_REPO_NAME):
    git.Git(".").clone(f"https://github.com/artsy/{TEST_GIT_REPO_NAME}.git")

@pytest.fixture(scope="session", autouse=True)
def cd_into_test_git_repo():
  os.chdir(TEST_GIT_REPO_NAME)

@pytest.fixture(autouse=True)
def test_git_repo_name():
  return TEST_GIT_REPO_NAME
