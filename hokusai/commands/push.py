import os

from hokusai.command import command
from hokusai.config import config
from hokusai.ecr import ECR
from hokusai.common import print_red, print_green, shout

@command
def push(tag):
  docker_compose_yml = os.path.join(os.getcwd(), 'hokusai/common.yml')
  shout("docker-compose -f %s -p build build" % docker_compose_yml, print_output=True)
  build = "build_%s:latest" % config.project_name

  ecr = ECR()
  if not ecr.project_repository_exists():
    print_red("ECR repository %s does not exist... did you run `hokusai setup` for this project?" % config.project_name)
    return -1

  if tag is None:
    tag = shout('git rev-parse HEAD')

  shout(ecr.get_login())

  shout("docker tag %s %s:%s" % (build, config.aws_ecr_registry, tag))
  shout("docker push %s:%s" % (config.aws_ecr_registry, tag))
  print_green("Pushed %s to %s:%s" % (build, config.aws_ecr_registry, tag))

  shout("docker tag %s %s:%s" % (build, config.aws_ecr_registry, 'latest'))
  shout("docker push %s:%s" % (config.aws_ecr_registry, 'latest'))
  print_green("Updated tag %s:%s -> %s:%s" %
      (config.aws_ecr_registry, tag, config.aws_ecr_registry, 'latest'))
