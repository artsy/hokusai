from hokusai.lib.command import command
from hokusai.lib.common import print_green
from hokusai.services.deployment import Deployment

@command
def deploy(context, tag, skip_tags):
  deployment = Deployment(context)
  deployment.update(tag, skip_tags)
  print_green("Deployment updated to %s" % tag)
