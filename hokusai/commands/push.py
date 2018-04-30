import os

from hokusai.lib.command import command
from hokusai.lib.config import config
from hokusai.services.ecr import ECR
from hokusai.lib.common import print_green, shout
from hokusai.lib.exceptions import HokusaiError

@command
def push(tag, build, force, overwrite):
  if force is None and shout('git status --porcelain'):
    raise HokusaiError("Working directory is not clean.  Aborting.")

  if force is None and shout('git status --porcelain --ignored'):
    raise HokusaiError("Working directory contains ignored files and/or directories.  Aborting.")

  ecr = ECR()
  if not ecr.project_repo_exists():
    raise HokusaiError("ECR repo %s does not exist... did you run `hokusai setup` for this project?" % config.project_name)

  shout(ecr.get_login())
  if tag is None:
    tag = shout('git rev-parse HEAD').strip()

  if overwrite is None and ecr.tag_exists(tag):
    raise HokusaiError("Tag %s already exists in registry.  Aborting." % tag)

  if build:
    docker_compose_yml = os.path.join(os.getcwd(), 'hokusai/common.yml')
    shout("docker-compose -f %s -p hokusai build" % docker_compose_yml, print_output=True)

  build_tag = "hokusai_%s:latest" % config.project_name

  shout("docker tag %s %s:%s" % (build_tag, config.docker_repo, tag))
  shout("docker push %s:%s" % (config.docker_repo, tag), print_output=True)
  print_green("Pushed %s to %s:%s" % (build_tag, config.docker_repo, tag))

  shout("docker tag %s %s:%s" % (build_tag, config.docker_repo, 'latest'))
  shout("docker push %s:%s" % (config.docker_repo, 'latest'), print_output=True)
  print_green("Pushed %s to %s:%s" % (build_tag, config.docker_repo, 'latest'))
