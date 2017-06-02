from hokusai.lib.command import command
from hokusai.lib.common import print_green
from hokusai.services.deployment import Deployment

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
