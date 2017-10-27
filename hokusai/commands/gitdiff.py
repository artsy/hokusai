from hokusai.lib.command import command
from hokusai.lib.common import print_green, shout
from hokusai.services.deployment import Deployment
from hokusai.services.ecr import ECR
from hokusai.lib.exceptions import HokusaiError

@command
def gitdiff():
  ecr = ECR()

  staging_deployment = Deployment('staging')
  staging_tag = staging_deployment.current_tag
  if staging_tag is None:
    raise HokusaiError("Could not find a tag 'staging'.  Aborting.")
  if staging_tag == 'staging':
    staging_tag = ecr.find_git_sha1_image_tag('staging')
    if staging_tag is None:
      raise HokusaiError("Could not find a git SHA1 tag for 'staging'.  Aborting.")

  production_deployment = Deployment('production')
  production_tag = production_deployment.current_tag
  if production_tag is None:
    raise HokusaiError("Could not find a tag 'production'.  Aborting.")
  if production_tag == 'production':
    production_tag = ecr.find_git_sha1_image_tag('production')
    if production_tag is None:
      raise HokusaiError("Could not find a git SHA1 tag for 'production'.  Aborting.")

  print_green("Comparing %s to %s" % (production_tag, staging_tag))
  shout("git diff %s %s" % (production_tag, staging_tag), print_output=True)
