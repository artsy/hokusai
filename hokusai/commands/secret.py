import os
import base64

from collections import OrderedDict
from subprocess import check_output, CalledProcessError, STDOUT
from tempfile import NamedTemporaryFile

import yaml

from hokusai.config import HokusaiConfig
from hokusai.common import print_red, print_green

def add_secret(context, key, value):
  config = HokusaiConfig().check()

  try:
    switch_context_result = check_output("kubectl config use-context %s" % context, stderr=STDOUT, shell=True)
    print_green("Switched context to %s" % context)
    if 'no context exists' in switch_context_result:
      print_red("Context %s does not exist.  Check ~/.kube/config" % context)
      return -1
    elif 'switched to context' in switch_context_result:
      try:
        existing_secrets = check_output("kubectl get secret %s-secrets -o yaml" % config.project_name, stderr=STDOUT, shell=True)
        secret_data = yaml.load(existing_secrets)['data']
      except CalledProcessError:
        secret_data = {}

      secret_data.update({key: base64.b64encode(value)})

      secret_yaml = OrderedDict([
        ('apiVersion', 'v1'),
        ('kind', 'Secret'),
        ('metadata', {
          'labels': {'app': config.project_name},
          'name': "%s-secrets" % config.project_name
        }),
        ('type', 'Opaque'),
        ('data', secret_data)
      ])

      f = NamedTemporaryFile(delete=False)
      f.write(yaml.safe_dump(secret_yaml, default_flow_style=False))
      f.close()
      check_output("kubectl apply -f %s" % f.name, stderr=STDOUT, shell=True)
      os.unlink(f.name)

  except CalledProcessError:
    print_red('Create secret failed')
    return -1

  print_green("Secret %s created" % key)
  return 0
