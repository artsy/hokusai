import os

from hokusai.lib.command import command
from hokusai.lib.config import config
from hokusai.services.ecr import ECR
from hokusai.lib.common import print_green, shout
from hokusai.lib.exceptions import HokusaiError
from hokusai.services.docker import Docker

@command()
def push(tag, local_tag, build, filename, force, overwrite, skip_latest=False):
  if force is None and shout('git status --porcelain'):
    raise HokusaiError("Working directory is not clean.  Aborting.")

  if force is None and shout('git status --porcelain --ignored'):
    raise HokusaiError("Working directory contains ignored files and/or directories.  Aborting.")

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
