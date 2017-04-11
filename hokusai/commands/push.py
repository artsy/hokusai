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
  shout(ECR().get_login())
  shout("docker tag %s %s:%s" % (build, config.aws_ecr_registry, tag))
  shout("docker push %s:%s" % (config.aws_ecr_registry, tag))
  print_green("Pushed %s to %s:%s" % (build, config.aws_ecr_registry, tag))
