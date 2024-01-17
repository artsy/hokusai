import os
import subprocess

from git import Repo
from packaging.specifiers import SpecifierSet
from packaging.version import Version

from hokusai.lib.common import ansi_escape


# tests operate on a test git repo
# repo is cloned in conftest.py
# working directory is set to repo dir, also in conftest.py

def describe_git_repo_for_test():
  def operating_in_test_git_repo_clone_dir(test_git_repo_name):
    assert os.path.basename(os.getcwd()) == test_git_repo_name
  def operating_on_main_branch():
    repo = Repo(os.getcwd())
    heads = repo.heads
    assert 'main' in heads

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
