import os
import base64
import json

import yaml

from hokusai.command import command
from hokusai.config import HokusaiConfig
from hokusai.common import print_red, print_green, shout, returncode, k8s_uuid, select_context

@command
def run(context, command, tag, env):
  config = HokusaiConfig().check()

  select_context(context)

  if tag is not None:
    image_tag = tag
  else:
    image_tag = context

  environment = map(lambda x: {"name": x.split('=')[0], "value": x.split('=')[1]}, env)
  existing_secrets = shout("kubectl get secret %s-secrets -o yaml" % config.project_name)
  secret_data = yaml.load(existing_secrets)['data']
  for k, v in secret_data.iteritems():
    environment.append({"name": k, "value": base64.b64decode(v)})

  if os.environ.get('USER') is not None:
    job_id = "%s-%s" % (os.environ.get('USER'), k8s_uuid())
  else:
    job_id = k8s_uuid()

  job_name = "%s-run-%s" % (config.project_name, job_id)
  image_name = "%s:%s" % (config.aws_ecr_registry, image_tag)

  overrides = {
    "apiVersion": "v1",
    "spec": {
      "containers": [
        {
          "args": command.split(' '),
          "name": job_name,
          "image": image_name,
          "imagePullPolicy": "Always",
          "env": environment
        }
      ]
    }
  }
  return returncode("kubectl run %s --attach --image=%s --overrides='%s' --restart=Never --rm" %
                  (job_name, image_name, json.dumps(overrides)))
