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

  pods = kctl.get_object('pod', selector="app=%s" % config.project_name)
  pods = filter(lambda pod: pod['status']['phase'] == 'Running', pods)

  if follow:
    processes = [Popen(kctl.command("logs %s %s%s" % (pod['metadata']['name'], config.project_name, opts)), shell=True) for pod in pods]
    try:
      for p in processes:
        p.wait()
    except KeyboardInterrupt:
      for p in processes:
        p.terminate()
  else:
    for pod in pods:
      shout(kctl.command("logs %s %s%s" % (pod['metadata']['name'], config.project_name, opts)), print_output=True)
