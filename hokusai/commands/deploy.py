from hokusai.lib.command import command
from hokusai.lib.common import print_green
from hokusai.services.deployment import Deployment

@command
def deploy(context, tag):
  deployment = Deployment(context)
  deployment.update(tag)
  print_green("Deployment updated to %s" % tag)
