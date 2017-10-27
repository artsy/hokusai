from hokusai.lib.command import command
from hokusai.lib.common import print_green
from hokusai.services.deployment import Deployment
from hokusai.services.command_runner import CommandRunner
from hokusai.lib.exceptions import HokusaiError

@command
def update(context, tag, migration, constraint):
  if migration is not None:
    print_green("Running migration '%s' on %s..." % (migration, context))
    return_code = CommandRunner(context).run(tag, migration, constraint=constraint)
    if return_code:
      raise HokusaiError("Migration failed with return code %s" % return_code, return_code=return_code)
  Deployment(context).update(tag, constraint)
  print_green("Deployment updated to %s" % tag)


@command
def history(context):
  deployment = Deployment(context)
  for name in deployment.names:
    print_green(name)
    print("REVISION    CREATION TIMESTAMP            CONTAINER NAME - IMAGE TAG")
    for replicaset in deployment.history(name):
      revision = replicaset['metadata']['annotations']['deployment.kubernetes.io/revision']
      created_at = replicaset['metadata']['creationTimestamp']
      containers = ["%s - %s" % (container['name'], container['image'].rsplit(':', 1)[1]) for container in replicaset['spec']['template']['spec']['containers']]
      print("%s           %s          %s" % (revision, created_at, ','.join(containers)))


@command
def refresh(context):
  deployment = Deployment(context)
  deployment.refresh()


@command
def promote(migration, constraint):
  deploy_from = Deployment('staging')
  tag = deploy_from.current_tag
  if tag is None:
    return -1
  print_green("Deploying tag %s to production..." % tag)
  if migration is not None:
    print_green("Running migration '%s' on production..." % migration)
    return_code = CommandRunner('production').run(tag, migration, constraint=constraint)
    if return_code:
      raise HokusaiError("Migration failed with return code %s" % return_code, return_code=return_code)
  deploy_to = Deployment('production').update(tag, constraint)
  print_green("Promoted staging to production at %s" % tag)
