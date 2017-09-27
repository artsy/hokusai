from hokusai.lib.config import config
from hokusai.lib.command import command
from hokusai.lib.common import print_red, print_green
from hokusai.services.deployment import Deployment
from hokusai.services.command_runner import CommandRunner

@command
def deploy(context, tag, migration, constraint):
  if migration is not None:
    print_green("Running migration '%s' on %s..." % (migration, context))
    retval = CommandRunner(context).run(tag, migration, constraint=constraint)
    if retval != 0:
      print_red("Migration failed with return code %s" % retval)
      return retval

  if config.before_deploy is not None:
    print_green("Running before-deploy hook '%s' on %s..." % (config.before_deploy, context))
    retval = CommandRunner(context).run(tag, config.before_deploy, constraint=constraint)
    if retval != 0:
      print_red("Command failed with return code %s" % retval)
      return retval

  deployment = Deployment(context)
  deployment.update(tag)

  if config.after_deploy is not None:
    print_green("Running after-deploy hook '%s' on %s..." % (config.after_deploy, context))
    retval = CommandRunner(context).run(tag, config.after_deploy, constraint=constraint)
    if retval != 0:
      print_red("Command failed with return code %s" % retval)
      return retval

  print_green("Deployment updated to %s" % tag)
