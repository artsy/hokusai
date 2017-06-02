import os
import base64
import json

import yaml

from hokusai.lib.command import command
from hokusai.lib.config import config
from hokusai.lib.common import shout, returncode, k8s_uuid
from hokusai.services.kubectl import Kubectl

@command
def run(context, command, tty, tag, env):
  kctl = Kubectl(context)

  if tag is not None:
    image_tag = tag
  else:
    image_tag = context

  if os.environ.get('USER') is not None:
    uuid = "%s-%s" % (os.environ.get('USER'), k8s_uuid())
  else:
    uuid = k8s_uuid()

  name = "%s-hokusai-run-%s" % (config.project_name, uuid)
  image_name = "%s:%s" % (config.aws_ecr_registry, image_tag)

  if tty:
    overrides = {
      "apiVersion": "v1",
      "spec": {
        "containers": [
          {
            "args": command.split(' '),
            "name": name,
            "image": image_name,
            "imagePullPolicy": "Always",
            'envFrom': [{'configMapRef': {'name': "%s-environment" % config.project_name}}],
            "stdin": True,
            "stdinOnce": True,
            "tty": True
          }
        ]
      }
    }
    shout(kctl.command("run %s -t -i --image=%s --restart=Never --overrides='%s' --rm" %
                   (name, image_name, json.dumps(overrides))), print_output=True)
  else:
    overrides = {
      "apiVersion": "v1",
      "spec": {
        "containers": [
          {
            "args": command.split(' '),
            "name": name,
            "image": image_name,
            "imagePullPolicy": "Always",
            'envFrom': [{'configMapRef': {'name': "%s-environment" % config.project_name}}]
          }
        ]
      }
    }
    return returncode(kctl.command("run %s --attach --image=%s --overrides='%s' --restart=Never --rm" %
                                      (name, image_name, json.dumps(overrides))))
