from hokusai.command import command
from hokusai.common import print_green
from hokusai.deployment import Deployment

@command
def promote(from_context, context):
  deploy_from = Deployment(from_context)
  tag = deploy_from.current_tag
  if tag is None:
    return -1

  deploy_to = Deployment(context)
  deploy_to.update(tag)
  print_green("Promoted %s to %s from %s" % (context, tag, from_context))
