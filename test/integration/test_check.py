import os

from git import Repo


# tests operate on a test git repo
# repo is cloned in conftest.py
# working directory is set to repo dir, also in conftest.py

def describe_git_repo_for_test():
  def dir_exists(test_git_repo_name):
    assert os.path.basename(os.getcwd()) == test_git_repo_name
  def on_main_branch():
    repo = Repo(os.getcwd())
    heads = repo.heads
    assert 'main' in heads
