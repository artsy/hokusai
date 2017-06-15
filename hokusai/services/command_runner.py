import os
import json

from hokusai.lib.config import config
from hokusai.lib.common import shout, returncode, k8s_uuid
from hokusai.services.kubectl import Kubectl

class CommandRunner(object):
  def __init__(self, context):
    self.context = context
    self.kctl = Kubectl(self.context)

  def run(self, image_tag, cmd, tty=False, env=()):
    if os.environ.get('USER') is not None:
      uuid = "%s-%s" % (os.environ.get('USER'), k8s_uuid())
    else:
      uuid = k8s_uuid()

    name = "%s-hokusai-run-%s" % (config.project_name, uuid)
    image_name = "%s:%s" % (config.aws_ecr_registry, image_tag)
    container = {
      "args": cmd.split(' '),
      "name": name,
      "image": image_name,
      "imagePullPolicy": "Always",
      'envFrom': [{'configMapRef': {'name': "%s-environment" % config.project_name}}]
    }

    if tty:
      container.update({
        "stdin": True,
        "stdinOnce": True,
        "tty": True
      })

    if len(env):
      container['env'] = []
      for s in env:
        if '=' not in s:
          print_red("Error: environment variables must be of the form 'KEY=VALUE'")
          return -1
        split = s.split('=', 1)
        container['env'].append({'name': split[0], 'value': split[1]})

    overrides = {
      "apiVersion": "v1",
      "spec": {
        "containers": [container]
      }
    }

    if tty:
      shout(self.kctl.command("run %s -t -i --image=%s --restart=Never --overrides='%s' --rm" %
                     (name, image_name, json.dumps(overrides))), print_output=True)
    else:
      return returncode(self.kctl.command("run %s --attach --image=%s --overrides='%s' --restart=Never --rm" %
                                        (name, image_name, json.dumps(overrides))))
