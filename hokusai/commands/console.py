import os
import base64
import json

from subprocess import call, check_output, CalledProcessError, STDOUT

import yaml

from hokusai.config import HokusaiConfig
from hokusai.common import print_red, print_green, k8s_uuid, verbose, select_context, HokusaiCommandError

def console(context, shell, tag, with_config, with_secrets, env):
  config = HokusaiConfig().check()

  try:
    select_context(context)
  except HokusaiCommandError, e:
    print_red(repr(e))
    return -1

  if tag is not None:
    image_tag = tag
  else:
    image_tag = context

  environment = map(lambda x: {"name": x.split('=')[0], "value": x.split('=')[1]}, env)

  if with_config:
    try:
      existing_configmap = check_output(verbose("kubectl get configmap %s-config -o yaml"
                                                  % config.project_name), stderr=STDOUT, shell=True)
      configmap_data = yaml.load(existing_configmap)['data']
    except CalledProcessError, e:
      if 'Error from server: configmaps "%s-config" not found' % config.project_name in e.output:
        configmap_data = {}
      else:
        print_red("Error fetching config: %s" % e.output)
        return -1

    for k, v in configmap_data.iteritems():
      environment.append({"name": k, "value": v})

  if with_secrets:
    try:
      existing_secrets = check_output(verbose("kubectl get secret %s-secrets -o yaml"
                                              % config.project_name), stderr=STDOUT, shell=True)
      secret_data = yaml.load(existing_secrets)['data']
    except CalledProcessError, e:
      if 'Error from server: secrets "%s-secrets" not found' % config.project_name in e.output:
        secret_data = {}
      else:
        print_red("Error fetching secrets: %s" % e.output)
        return -1

    for k, v in secret_data.iteritems():
      try:
        environment.append({"name": k, "value": base64.b64decode(v)})
      except TypeError:
        continue

  if os.environ.get('USER') is not None:
    job_id = "%s-%s" % (os.environ.get('USER'), k8s_uuid())
  else:
    job_id = k8s_uuid()

  job_name = "%s-shell-%s" % (config.project_name, job_id)
  image_name = "%s:%s" % (config.aws_ecr_registry, image_tag)

  overrides = {
    "apiVersion": "batch/v1",
    "spec": {
      "template": {
        "spec": {
          "containers": [
            {
              "args": [ shell ],
              "name": job_name,
              "image": image_name,
              "imagePullPolicy": "Always",
              "env": environment,
              "stdin": True,
              "stdinOnce": True,
              "tty": True
            }
          ]
        }
      }
    }
  }

  try:
    call(verbose("kubectl run %s -t -i --image=%s --restart=OnFailure --overrides='%s' --rm" %
             (job_name, image_name, json.dumps(overrides))), shell=True)
  except CalledProcessError, e:
    print_red("Launching console failed with error %s" % e.output)
    return -1
