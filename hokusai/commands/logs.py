from subprocess import Popen

from hokusai.lib.command import command
from hokusai.lib.config import config
from hokusai.lib.common import shout
from hokusai.services.kubectl import Kubectl

@command
def logs(context, timestamps, nlines, follow):
  kctl = Kubectl(context)

  opts = ''
  if timestamps:
    opts += ' --timestamps'
  if nlines:
    opts += " --tail=%s" % nlines
  if follow:
    opts += ' --follow'

  pods = kctl.get_object('pod', selector="app=%s,layer=application" % config.project_name)
  pods = filter(lambda pod: pod['status']['phase'] == 'Running', pods)
  containers = []
  for pod in pods:
    for container in pod['spec']['containers']:
      containers.append({'pod': pod['metadata']['name'], 'name': container['name']})

  # Concurrent
  processes = [Popen(kctl.command("logs %s %s%s" % (container['pod'], container['name'], opts)), shell=True) for container in containers]
  success = []
  try:
    for p in processes:
      success.append(p.wait())
  except KeyboardInterrupt:
    for p in processes:
      p.terminate()
      return -1

  for retval in success:
    if retval != 0:
      return retval
