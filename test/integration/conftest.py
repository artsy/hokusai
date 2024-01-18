import os
import re
import shutil
import subprocess

import git
import pytest

from hokusai.lib.common import ansi_escape


TEST_GIT_REPO_NAME = 'hokusai-integration-test'


def exit_pytest_if_not_minikube(context):
  ''' exit pytest if context is likely not minikube '''
  resp = subprocess.run(
    f'kubectl --context {context} cluster-info',
    capture_output=True,
    shell=True,
    text=True,
    timeout=5
  )
  p = re.compile(r'Kubernetes control plane is running at https://(.*)')
  m = p.search(ansi_escape(resp.stdout))
  control_plane_address = m.groups()[0]
  # 127.0.0.1 = local
  # 192.168.x.y = circleci
  if not (
    control_plane_address.startswith('127.0.0.1') or
    control_plane_address.startswith('192.168')
  ):
    msg = f'Error: {context} context possibly points to a real cluster. Is it a Minikube instance?'
    pytest.exit(msg)

def pytest_configure(config):
  ''' do things before tests '''
  # make sure to not operate on real Staging and Production clusters
  exit_pytest_if_not_minikube('staging')
  exit_pytest_if_not_minikube('production')
  # clone test git repo
  os.chdir('test/integration/fixtures')
  # skip cloning if already cloned and no force
  if os.path.isdir(TEST_GIT_REPO_NAME) and os.environ.get('FORCE_CLONE') != '1':
    return
  shutil.rmtree(TEST_GIT_REPO_NAME)
  git.Git(".").clone(f"https://github.com/artsy/{TEST_GIT_REPO_NAME}.git")


## autouse fixtures

@pytest.fixture(scope="session", autouse=True)
def cd_into_test_git_repo():
  os.chdir(TEST_GIT_REPO_NAME)

@pytest.fixture(autouse=True)
def test_git_repo_name():
  return TEST_GIT_REPO_NAME
