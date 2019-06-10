import os

from hokusai.lib.command import command
from hokusai.lib.config import config
from hokusai.services.ecr import ECR
from hokusai.lib.common import print_green, shout
from hokusai.lib.exceptions import HokusaiError

@command()
def pull(tag, local_tag):
  ecr = ECR()
  if not ecr.project_repo_exists():
    raise HokusaiError("ECR repo %s does not exist... did you run `hokusai setup` for this project?" % config.project_name)

  shout(ecr.get_login(), mask=(r'^(docker login -u) .+ (-p) .+ (.+)$', r'\1 ****** \2 ***** \3'))

  shout("docker pull %s:%s" % (ecr.project_repo, tag))

  shout("docker tag %s:%s hokusai_%s:%s" % (ecr.project_repo, tag, config.project_name, local_tag))
  
  print_green("Pulled %s:%s to hokusai_%s:%s" % (ecr.project_repo, tag, config.project_name, local_tag), newline_after=True)
