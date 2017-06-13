from hokusai.lib.command import command
from hokusai.lib.common import print_red, print_green
from hokusai.services.deployment import Deployment
from hokusai.services.command_runner import CommandRunner

@command
def promote(migration):
  deploy_from = Deployment('staging')
  tag = deploy_from.current_tag
  if tag is None:
    return -1

  if migration is not None:
    retval = CommandRunner('production').run(tag, migration)
    if retval != 0:
      print_red("Migration failed with return code %s" % retval)
      return retval

  deploy_to = Deployment('production')
  deploy_to.update(tag)
  print_green("Promoted staging to production from %s" % tag)
