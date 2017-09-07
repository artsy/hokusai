from hokusai.lib.command import command
from hokusai.lib.common import print_red, print_green, shout
from hokusai.services.deployment import Deployment
from hokusai.services.ecr import ECR

@command
def diff(pr_only=False):
  ecr = ECR()

  staging_deployment = Deployment('staging')
  staging_tag = staging_deployment.current_tag
  if staging_tag is None:
    return -1
  if staging_tag == 'staging':
    staging_tag = ecr.find_git_sha1_image_tag('staging')
    if staging_tag is None:
      print_red("Cound not find a git SHA1 tag for 'staging'.  Aborting.")
      return -1

  production_deployment = Deployment('production')
  production_tag = production_deployment.current_tag
  if production_tag is None:
    return -1
  if production_tag == 'production':
    production_tag = ecr.find_git_sha1_image_tag('production')
    if production_tag is None:
      print_red("Cound not find a git SHA1 tag for 'production'.  Aborting.")
      return -1

  print_green("Comparing %s to %s" % (production_tag, staging_tag))
  if pr_only:
    shout("git log --merges --right-only %s..%s" % (production_tag, staging_tag), print_output=True)
  else:
    shout("git diff %s %s" % (production_tag, staging_tag), print_output=True)
