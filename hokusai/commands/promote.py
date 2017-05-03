from hokusai.lib.command import command
from hokusai.lib.common import print_green
from hokusai.services.deployment import Deployment

@command
def promote():
  deploy_from = Deployment('staging')
  tag = deploy_from.current_tag
  if tag is None:
    return -1

  deploy_to = Deployment('production')
  deploy_to.update(tag)
  print_green("Promoted staging to production from %s" % tag)
