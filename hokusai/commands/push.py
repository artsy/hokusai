import os
import pdb

from hokusai.lib.command import command
from hokusai.lib.config import config
from hokusai.services.ecr import ECR
from hokusai.lib.common import print_green, print_red, shout
from hokusai.lib.exceptions import HokusaiError
from hokusai.services.docker import Docker

@command()
def push(tag, local_tag, build, filename, force, overwrite, skip_latest=False):
  if not force:
    git_unclean_files = shout('git status --porcelain --ignored')
    if git_unclean_files:
      print_red("The following files/directories are either changed, untracked, or ignored.")
      print_red("If they are not excluded by .dockerignore, they may get copied into the resulting Docker image.")
      print(git_unclean_files)
      raise HokusaiError("Aborting. Re-run command with --force flag, if you are not concerned.")

  ecr = ECR()
  if not ecr.project_repo_exists():
    raise HokusaiError("ECR repo %s does not exist... did you run `hokusai setup` for this project?" % config.project_name)

  shout(ecr.get_login(), mask=(r'^(docker login -u) .+ (-p) .+ (.+)$', r'\1 ****** \2 ***** \3'))
  if tag is None:
    tag = shout('git rev-parse HEAD').strip()

  if overwrite is None and ecr.tag_exists(tag):
    raise HokusaiError("Tag %s already exists in registry.  Aborting." % tag)

  if build:
    Docker().build()

  build_tag = "hokusai_%s:%s" % (config.project_name, local_tag)

  shout("docker tag %s %s:%s" % (build_tag, ecr.project_repo, tag))
  shout("docker push %s:%s" % (ecr.project_repo, tag), print_output=True)
  print_green("Pushed %s to %s:%s" % (build_tag, ecr.project_repo, tag), newline_after=True)

  if skip_latest: return

  shout("docker tag %s %s:%s" % (build_tag, ecr.project_repo, 'latest'))
  shout("docker push %s:%s" % (ecr.project_repo, 'latest'), print_output=True)
  print_green("Pushed %s to %s:%s" % (build_tag, ecr.project_repo, 'latest'), newline_after=True)
