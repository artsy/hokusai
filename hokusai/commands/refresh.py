from hokusai.lib.command import command
from hokusai.lib.common import print_green
from hokusai.services.deployment import Deployment

@command
def refresh(context):
  deployment = Deployment(context)
  deployment.refresh()
