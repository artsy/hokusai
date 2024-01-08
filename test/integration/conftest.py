import os

import git
import pytest


INTEGRATION_FIXTURES_DIR = 'test/integration/fixtures'
TEST_GIT_REPO_NAME = 'hokusai-sandbox'

@pytest.fixture(scope="session", autouse=True)
def clone_repo():
  os.chdir(INTEGRATION_FIXTURES_DIR)
  # avoid cloning repeatedly when on local
  if not os.path.isdir(TEST_GIT_REPO_NAME):
    git.Git(".").clone(f"https://github.com/artsy/{TEST_GIT_REPO_NAME}.git")
  os.chdir(TEST_GIT_REPO_NAME)

@pytest.fixture(autouse=True)
def test_git_repo_name():
  return TEST_GIT_REPO_NAME
