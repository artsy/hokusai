from hokusai.lib.command import command
from hokusai.lib.common import print_red, print_green
from hokusai.services.deployment import Deployment
from hokusai.services.command_runner import CommandRunner

@command
def deploy(context, tag, migration, constraint):
  if migration is not None:
    print_green("Running migration '%s' on %s..." % (migration, context))
    retval = CommandRunner(context).run(tag, migration, constraint=constraint)
    if retval:
      print_red("Migration failed with return code %s" % retval)
      return retval

  deployment = Deployment(context)
  retval = deployment.update(tag, constraint)
  if retval is not None:
    return retval
  print_green("Deployment updated to %s" % tag)
