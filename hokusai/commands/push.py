import os
import pdb

from hokusai.lib.command import command
from hokusai.lib.config import config
from hokusai.services.ecr import ECR
from hokusai.lib.common import print_green, print_red, shout
from hokusai.lib.exceptions import HokusaiError
from hokusai.services.docker import Docker

@command()
def build_and_push(remote_tag, local_tag, filename, ecr, skip_latest=False):
  Docker().build(filename)
  push(remote_tag, local_tag, ecr, skip_latest)

def ecr_check():
  ecr = ECR()
  if not ecr.project_repo_exists():
    raise HokusaiError("ECR repo %s does not exist... did you run `hokusai setup` for this project?" % config.project_name)
  return ecr

@command()
def git_status_check():
  git_unclean_files = shout('git status --porcelain --ignored')
  if git_unclean_files:
    print_red("The following files/directories are either changed, untracked, or ignored.")
    print_red("If they are not excluded by .dockerignore, they may get copied into the resulting Docker image.")
    print(git_unclean_files)
    raise HokusaiError("Aborting. Re-run command with --force flag, if you are confident.")

@command()
def push(remote_tag, local_tag, ecr, skip_latest=False):
  shout(ecr.get_login(), mask=(r'^(docker login -u) .+ (-p) .+ (.+)$', r'\1 ****** \2 ***** \3'))
  docker_compose_repo = "hokusai_" + config.project_name
  tag_and_push(docker_compose_repo, local_tag, ecr.project_repo, remote_tag)
  if not skip_latest:
    tag_and_push(docker_compose_repo, local_tag, ecr.project_repo, 'latest')

def remote_tag_check(remote_tag, overwrite, ecr):
  if remote_tag is None:
    remote_tag = shout('git rev-parse HEAD').strip()
  if not overwrite and ecr.tag_exists(remote_tag):
    raise HokusaiError("Tag %s already exists in registry.  Aborting." % remote_tag)
  return remote_tag

def tag_and_push(local_repo, local_tag, remote_repo, remote_tag):
  shout("docker tag %s:%s %s:%s" % (local_repo, local_tag, remote_repo, remote_tag))
  shout("docker push %s:%s" % (remote_repo, remote_tag), print_output=True)
  print_green("Pushed %s:%s to %s:%s" % (local_repo, local_tag, remote_repo, remote_tag), newline_after=True)
