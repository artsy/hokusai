from hokusai.command import command
from hokusai.common import print_green
from hokusai.deployment import Deployment

@command
def deploy(context, tag):
  deployment = Deployment(context)
  deployment.update(tag)
  print_green("Deployment updated to %s" % tag)
