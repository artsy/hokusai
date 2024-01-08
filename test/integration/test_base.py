import os

from git import Repo
from packaging.specifiers import SpecifierSet
from packaging.version import Version
from subprocess import check_output

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

def describe_version():
  def it_outputs_valid_version():
    output = check_output('hokusai version', shell=True, text=True, timeout=5)
    spec1 = SpecifierSet('>=0.0.0', prereleases=True)
    version_output = ansi_escape(output.rstrip())
    assert Version(version_output) in spec1

def describe_check():
  def it_validates_aws_creds():
    output = None
    try:
      output = check_output('hokusai check', shell=True, text=True, timeout=5)
      assert 'Valid AWS credentials found' in output
    except:
      print(output)
      raise
