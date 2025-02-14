import os
import pytest
import subprocess

from git import Repo
from packaging.specifiers import SpecifierSet
from packaging.version import Version

from hokusai.lib.common import ansi_escape


# tests operate on a test git repo
# repo is cloned in conftest.py
# working directory is set to repo dir, also in conftest.py


@pytest.mark.order(110)
def describe_git_repo_for_test():
  def operating_in_test_git_repo_clone_dir(name_of_test_git_repo):
    assert os.path.basename(os.getcwd()) == name_of_test_git_repo
  def operating_on_main_branch():
    repo = Repo(os.getcwd())
    heads = repo.heads
    assert 'main' in heads

@pytest.mark.order(120)
def describe_hokusai_version():
  def it_outputs_valid_version():
    resp = subprocess.run(
      'hokusai version',
      capture_output=True,
      shell=True,
      text=True,
      timeout=5
    )
    if resp.returncode != 0:
      print(resp.stderr)
    assert resp.returncode == 0
    spec1 = SpecifierSet('>=0.0.0', prereleases=True)
    version_output = ansi_escape(resp.stdout.rstrip())
    assert Version(version_output) in spec1

@pytest.mark.order(130)
def describe_hokusai_check():
  def it_validates_aws_creds():
    resp = subprocess.run(
      'hokusai check',
      capture_output=True,
      shell=True,
      text=True,
      timeout=5
    )
    if resp.returncode != 0:
      print(resp.stderr)
    assert resp.returncode == 0
    assert 'Valid AWS credentials found' in resp.stdout
