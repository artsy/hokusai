from hokusai.lib.command import command
from hokusai.lib.common import print_green, shout
from hokusai.services.deployment import Deployment

@command
def diff():
  staging = Deployment('staging')
  staging_tag = staging.current_tag
  if staging_tag is None:
    return -1

  production = Deployment('production')
  production_tag = production.current_tag
  if production_tag is None:
    return -1

  print_green("Comparing %s to %s" % (production_tag, staging_tag))
  shout("git diff %s %s" % (production_tag, staging_tag), print_output=True)
