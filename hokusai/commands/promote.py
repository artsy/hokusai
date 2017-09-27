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
  print_green("Deploying tag %s to production..." % tag)

  if migration is not None:
    print_green("Running migration '%s' on production..." % migration)
    retval = CommandRunner('production').run(tag, migration)
    if retval != 0:
      print_red("Migration failed with return code %s" % retval)
      return retval

  deploy_to = Deployment('production')
  deploy_to.update(tag)
  print_green("Promoted staging to production at %s" % tag)
