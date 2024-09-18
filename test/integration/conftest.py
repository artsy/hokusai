import os
import re
import shutil
import subprocess

import git
import pytest

from hokusai.lib.common import ansi_escape


CWD = os.getcwd()
NAME_OF_TEST_GIT_REPO = 'hokusai-integration-test'
FIXTURES_DIR = f'{CWD}/test/integration/fixtures'
TEST_REPO_DIR = f'{FIXTURES_DIR}/{NAME_OF_TEST_GIT_REPO}'


def apply_test_repo_serviceaccount(context, test_repo_dir):
  ''' apply test repo's k8s service account spec '''
  resp = subprocess.run(
    f'kubectl --context {context} apply -f {test_repo_dir}/hokusai/serviceaccount.yml',
    capture_output=True,
    shell=True,
    text=True,
    timeout=5
  )
  print(resp.stdout)
  print(resp.stderr)

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

# a hook called by Pytest for initial configuration
# https://docs.pytest.org/en/7.1.x/reference/reference.html#pytest.hookspec.pytest_configure
def pytest_configure(config):
  ''' do things before tests '''
  verbose()
  # make sure to not operate on real Staging and Production clusters
  exit_pytest_if_not_minikube('staging')
  exit_pytest_if_not_minikube('production')
  # get into fixtures dir, affects all tests
  os.chdir('test/integration/fixtures')
  # clone test repo if:
  # - local repo dir does not exist, or
  # - we force
  if not os.path.isdir(TEST_REPO_DIR) or os.environ.get('FORCE_CLONE') == '1':
    shutil.rmtree(TEST_REPO_DIR, ignore_errors=True)
    git.Git(FIXTURES_DIR).clone(f"https://github.com/artsy/{NAME_OF_TEST_GIT_REPO}.git")
  # apply service account spec
  apply_test_repo_serviceaccount('staging', TEST_REPO_DIR)
  apply_test_repo_serviceaccount('production', TEST_REPO_DIR)

def verbose():
  ''' verbose output to help with troubleshooting '''
  print(
  f'''
  current working directory: {CWD}
  test git repo: {NAME_OF_TEST_GIT_REPO}
  fixtures directory: {FIXTURES_DIR}
  test git repo directory: f{TEST_REPO_DIR}
  '''
  )

## autouse fixtures

@pytest.fixture(scope="session", autouse=True)
def cd_into_test_git_repo():
  os.chdir(TEST_REPO_DIR)

@pytest.fixture(autouse=True)
def name_of_test_git_repo():
  return NAME_OF_TEST_GIT_REPO
