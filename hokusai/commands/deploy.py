from hokusai.lib.command import command
from hokusai.lib.common import print_green
from hokusai.services.deployment import Deployment
from hokusai.services.command_runner import CommandRunner
from hokusai.lib.exceptions import HokusaiError

@command
def deploy(context, tag, migration, constraint):
  if migration is not None:
    print_green("Running migration '%s' on %s..." % (migration, context))
    return_code = CommandRunner(context).run(tag, migration, constraint=constraint)
    if return_code:
      raise HokusaiError("Migration failed with return code %s" % return_code, return_code=return_code)

  Deployment(context).update(tag, constraint)
  print_green("Deployment updated to %s" % tag)
