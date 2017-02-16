import os

from collections import OrderedDict
from subprocess import check_output, CalledProcessError, STDOUT

import yaml

from hokusai.config import HokusaiConfig
from hokusai.common import print_red, print_green

def pull_secrets(context):
  config = HokusaiConfig().check()

  try:
    switch_context_result = check_output("kubectl config use-context %s"
                                         % context, stderr=STDOUT, shell=True)
    print_green("Switched context to %s" % context)
    if 'no context exists' in switch_context_result:
      print_red("Context %s does not exist.  Check ~/.kube/config" % context)
      return -1
    elif 'switched to context' in switch_context_result:
      try:
        existing_secrets = check_output("kubectl get secret %s-secrets -o yaml"
                                        % config.project_name, stderr=STDOUT, shell=True)
        secret_data = yaml.load(existing_secrets)['data']
      except CalledProcessError, e:
        if 'Error from server: secrets "%s-secrets" not found' % config.project_name in e.output:
          secret_data = {}
        else:
          return -1

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

      with open(os.path.join(os.getcwd(), 'hokusai', "%s-secrets.yml" % context), 'w') as f:
        f.write(yaml.safe_dump(secret_yaml, default_flow_style=False))

  except CalledProcessError:
    print_red("Failed to pull hokusai/%s-secrets.yml" % context)
    return -1

  print_green("Pulled hokusai/%s-secrets.yml" % context)
  return 0

def push_secrets(context):
  config = HokusaiConfig().check()

  try:
    switch_context_result = check_output("kubectl config use-context %s"
                                         % context, stderr=STDOUT, shell=True)
    print_green("Switched context to %s" % context)
    if 'no context exists' in switch_context_result:
      print_red("Context %s does not exist.  Check ~/.kube/config" % context)
      return -1
    elif 'switched to context' in switch_context_result:
      check_output("kubectl apply -f %s" % os.path.join(os.getcwd(), 'hokusai', "%s-secrets.yml" % context), stderr=STDOUT, shell=True)

  except CalledProcessError:
    print_red("Failed to push hokusai/%s-secrets.yml" % context)
    return -1

  print_green("Pushed hokusai/%s-secrets.yml" % context)
  return 0
