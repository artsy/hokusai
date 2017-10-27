from hokusai.lib.command import command
from hokusai.lib.config import config
from hokusai.lib.common import shout, shout_concurrent
from hokusai.services.kubectl import Kubectl

@command
def logs(context, timestamps, follow, tail):
  kctl = Kubectl(context)

  opts = ''
  if timestamps:
    opts += ' --timestamps'
  if follow:
    opts += ' --follow'
  if tail:
    opts += " --tail=%s" % tail

  pods = kctl.get_object('pod', selector="app=%s,layer=application" % config.project_name)
  pods = filter(lambda pod: pod['status']['phase'] == 'Running', pods)
  containers = []

  for pod in pods:
    for container in pod['spec']['containers']:
      containers.append({'pod': pod['metadata']['name'], 'name': container['name']})

  commands = [kctl.command("logs %s %s%s" % (container['pod'], container['name'], opts)) for container in containers]
  return shout_concurrent(commands, print_output=True)
