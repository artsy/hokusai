import os
import sys
import base64

from collections import OrderedDict
from tempfile import NamedTemporaryFile

import yaml

from hokusai.command import command
from hokusai.config import config
from hokusai.common import print_red, print_green, shout, CalledProcessError
from hokusai.kubectl import Kubectl

@command
def get_secrets(context):
  kctl = Kubectl(context)
  existing_secrets = shout(kctl.command("get secret %s-secrets -o yaml" % config.project_name))
  secret_data = yaml.load(existing_secrets)['data']
  for k, v in secret_data.iteritems():
    print("%s=%s" % (k, base64.b64decode(v)))

@command
def set_secrets(context, secrets):
  kctl = Kubectl(context)
  try:
    existing_secrets = shout(kctl.command("get secret %s-secrets -o yaml" % config.project_name))
    secret_data = yaml.load(existing_secrets)['data']
  except CalledProcessError, e:
    if 'secrets "%s-secrets" not found' % config.project_name in e.output:
      secret_data = {}
    else:
      raise

  for secret in secrets:
    if '=' not in secret:
      print_red("Error: secrets must be of the form 'KEY=VALUE'")
      return -1

    split_secret = secret.split('=', 1)
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
  try:
    shout(kctl.command("apply -f %s" % f.name))
  finally:
    os.unlink(f.name)

@command
def unset_secrets(context, secrets):
  kctl = Kubectl(context)

  existing_secrets = shout(kctl.command("get secret %s-secrets -o yaml" % config.project_name))
  secret_data = yaml.load(existing_secrets)['data']
  for secret in secrets:
    try:
      del secret_data[secret]
    except KeyError:
      print_red("Cannot unset '%s' as it does not exist..." % secret)

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

  try:
    shout(kctl.command("apply -f %s" % f.name))
  finally:
    os.unlink(f.name)
