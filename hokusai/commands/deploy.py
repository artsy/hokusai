from hokusai.lib.command import command
from hokusai.lib.common import print_red, print_green
from hokusai.services.deployment import Deployment
from hokusai.services.command_runner import CommandRunner

@command
def deploy(context, tag, migration):
  if migration is not None:
    retval = CommandRunner(context).run(tag, migration)
    if retval != 0:
      print_red("Migration failed with return code %s" % retval)
      return retval

  deployment = Deployment(context)
  deployment.update(tag)
  print_green("Deployment updated to %s" % tag)
