from hokusai.lib.config import config
from hokusai.services.ecr import ECR
from hokusai.lib.common import print_green, print_yellow, shout
from hokusai.lib.exceptions import HokusaiError
from hokusai.services.docker import Docker

def build_and_push(remote_tag, local_tag, filename, ecr, skip_latest=False):
  """Build Docker image and push it to ECR"""
  Docker().build(filename)
  push_only(remote_tag, local_tag, ecr, skip_latest)

def ecr_check():
  """Check that ECR has a repo for the project"""
  ecr = ECR()
  if not ecr.project_repo_exists():
    raise HokusaiError("ECR repo %s does not exist. Has 'hokusai setup' been run for this project?" % config.project_name)
  return ecr

def git_status_check():
  """Check working directory's Git status"""
  git_status_files = shout('git status --porcelain --ignored')
  if git_status_files:
    print_yellow("The following files/directories are either changed, untracked, or Git ignored.")
    print_yellow("If they are not excluded by .dockerignore, they may get copied into the resulting Docker image.")
    print_yellow(git_status_files)
    raise HokusaiError("Working directory unclean. Aborting. Use '--force' to force.")

def push_image(remote_tag, local_tag, build, filename, force, overwrite, skip_latest=False):
  """Push Docker image to ECR"""
  force or git_status_check()
  ecr = ecr_check()
  remote_tag = remote_tag_check(remote_tag, overwrite, ecr)
  if build:
    build_and_push(remote_tag, local_tag, filename, ecr, skip_latest)
  else:
    push_only(remote_tag, local_tag, ecr, skip_latest)

def push_only(remote_tag, local_tag, ecr, skip_latest=False):
  """Push Docker Compose built image to ECR"""
  shout(ecr.get_login(), mask=(r'^(docker login -u) .+ (-p) .+ (.+)$', r'\1 ****** \2 ***** \3'))
  docker_compose_repo = "hokusai_" + config.project_name
  tag_and_push(docker_compose_repo, local_tag, ecr.project_repo, remote_tag)
  if not skip_latest:
    tag_and_push(docker_compose_repo, local_tag, ecr.project_repo, 'latest')

def remote_tag_check(remote_tag, overwrite, ecr):
  """Set the tag to be used in ECR and see whether it already exists there"""
  if remote_tag is None:
    remote_tag = shout('git rev-parse HEAD').strip()
  if not overwrite and ecr.tag_exists(remote_tag):
    raise HokusaiError("Tag %s already exists in registry. Aborting. Use '--overwrite' to overwrite registry's tag." % remote_tag)
  return remote_tag

def tag_and_push(local_repo, local_tag, remote_repo, remote_tag):
  """Push local Docker repo:tag to remote repo:tag"""
  shout("docker tag %s:%s %s:%s" % (local_repo, local_tag, remote_repo, remote_tag))
  shout("docker push %s:%s" % (remote_repo, remote_tag), print_output=True)
  print_green("Pushed %s:%s to %s:%s" % (local_repo, local_tag, remote_repo, remote_tag), newline_after=True)
