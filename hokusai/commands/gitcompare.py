from hokusai.lib.command import command
from hokusai.lib.common import print_red, print_green, shout
from hokusai.lib.config import config
from hokusai.services.deployment import Deployment
from hokusai.services.ecr import ECR
from hokusai.lib.exceptions import HokusaiError

@command()
def gitcompare(org_name, git_compare_link):
  ecr = ECR()

  staging_tag = ecr.find_git_sha1_image_tag('staging')
  if staging_tag is None:
    raise HokusaiError("Could not find a tag for staging.  Aborting.")

  production_tag = ecr.find_git_sha1_image_tag('production')
  if production_tag is None:
    raise HokusaiError("Could not find a git SHA1 tag for production.  Aborting.")

  print_green(git_compare_link % (org_name, config.project_name, production_tag, staging_tag))
