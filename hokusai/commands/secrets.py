import os
import base64

from collections import OrderedDict
from subprocess import check_output, CalledProcessError, STDOUT
from tempfile import NamedTemporaryFile

import yaml

from hokusai.config import HokusaiConfig
from hokusai.common import print_red, print_green

def get_secrets(context):
  config = HokusaiConfig().check()

  try:
    switch_context_result = check_output("kubectl config use-context %s"
                                         % context, stderr=STDOUT, shell=True)
    print_green("Switched context to %s" % context)
    if 'no context exists' in switch_context_result:
      print_red("Context %s does not exist.  Check ~/.kube/config" % context)
      return -1
    elif 'switched to context' in switch_context_result:
      existing_secrets = check_output("kubectl get secret %s-secrets -o yaml"
                                      % config.project_name, stderr=STDOUT, shell=True)
      secret_data = yaml.load(existing_secrets)['data']
      for k, v in secret_data.iteritems():
        print("%s=%s" % (k, base64.b64decode(v)))

  except CalledProcessError, e:
    print_red("Error: %s" % e.output)
    return -1
  return 0

def set_secrets(context, secrets):
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
          print("Secret %s-secrets not found. Creating..." % config.project_name)
          secret_data = {}
        else:
          print_red("Server error: %s" % e.output)
          return -1

      for secret in secrets:
        if '=' not in secret:
          print_red("Error: secrets must be of the form 'KEY=VALUE'")
          return -1
        split_secret = secret.split('=')
        secret_data.update({split_secret[0]: base64.b64encode(split_secret[1])})

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

  except CalledProcessError, e:
    print_red("Error: %s" % e.output)
    return -1
  return 0

def unset_secrets(context, secrets):
  config = HokusaiConfig().check()

  try:
    switch_context_result = check_output("kubectl config use-context %s"
                                         % context, stderr=STDOUT, shell=True)
    print_green("Switched context to %s" % context)
    if 'no context exists' in switch_context_result:
      print_red("Context %s does not exist.  Check ~/.kube/config" % context)
      return -1
    elif 'switched to context' in switch_context_result:
      existing_secrets = check_output("kubectl get secret %s-secrets -o yaml"
                                      % config.project_name, stderr=STDOUT, shell=True)
      secret_data = yaml.load(existing_secrets)['data']

      for secret in secrets:
        try:
          del secret_data[secret]
        except KeyError:
          print("Cannot unset '%s' as it does not exist..." % secret)

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

  except CalledProcessError, e:
    print_red("Error: %s" % e.output)
    return -1
  return 0
