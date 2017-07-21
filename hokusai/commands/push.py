import os

from hokusai.lib.command import command
from hokusai.lib.config import config
from hokusai.services.ecr import ECR
from hokusai.lib.common import print_red, print_green, shout

@command
def push(tag, force):
  if force is None and shout('git status --porcelain'):
    print_red("Working directory is not clean.  Aborting.")
    return -1

  ecr = ECR()
  if not ecr.project_repository_exists():
    print_red("ECR repository %s does not exist... did you run `hokusai setup` for this project?" % config.project_name)
    return -1

  shout(ecr.get_login())
  if tag is None:
    tag = shout('git rev-parse HEAD').strip()

  if force is None and ecr.tag_exists(tag):
    print_red("Tag %s already exists in remote repository.  Aborting." % tag)
    return -1

  docker_compose_yml = os.path.join(os.getcwd(), 'hokusai/common.yml')
  shout("docker-compose -f %s -p build build" % docker_compose_yml, print_output=True)
  build = "build_%s:latest" % config.project_name

  shout("docker tag %s %s:%s" % (build, config.aws_ecr_registry, tag))
  shout("docker push %s:%s" % (config.aws_ecr_registry, tag), print_output=True)
  print_green("Pushed %s to %s:%s" % (build, config.aws_ecr_registry, tag))

  shout("docker tag %s %s:%s" % (build, config.aws_ecr_registry, 'latest'))
  shout("docker push %s:%s" % (config.aws_ecr_registry, 'latest'), print_output=True)
  print_green("Pushed %s to %s:%s" % (build, config.aws_ecr_registry, 'latest'))
