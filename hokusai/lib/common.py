import signal
import string
import random
import json

from collections import OrderedDict

from subprocess import call, check_call, check_output, CalledProcessError, STDOUT

import yaml
import boto3

from termcolor import cprint

EXIT_SIGNALS = [signal.SIGHUP, signal.SIGINT, signal.SIGQUIT, signal.SIGPIPE, signal.SIGTERM]

YAML_HEADER = '---\n'

VERBOSE = False

def print_green(msg):
  cprint(msg, 'green')

def print_red(msg):
  cprint(msg, 'red')

def set_output(v):
  global VERBOSE
  VERBOSE = v

def verbose(msg):
  if VERBOSE: cprint("==> hokusai exec `%s`" % msg, 'yellow')
  return msg

def returncode(command):
  return call(verbose(command), stderr=STDOUT, shell=True)

def shout(command, print_output=False):
  if print_output:
    return check_call(verbose(command), stderr=STDOUT, shell=True)
  else:
    return check_output(verbose(command), stderr=STDOUT, shell=True)

def k8s_uuid():
  uuid = []
  for i in range(0,5):
    uuid.append(random.choice(string.lowercase))
  return ''.join(uuid)

def build_deployment(name, image, target_port, environment=None, always_pull=False):
  container = {
    'name': name,
    'image': image,
    'ports': [{'containerPort': target_port}],
    'envFrom': [{'configMapRef': {'name': "%s-environment" % name}}]
  }

  if environment is not None:
    container['env'] = environment

  if always_pull:
    container['imagePullPolicy'] = 'Always'

  deployment = OrderedDict([
    ('apiVersion', 'extensions/v1beta1'),
    ('kind', 'Deployment'),
    ('metadata', {'name': name}),
    ('spec', {
      'replicas': 1,
      'template': {
        'metadata': {
          'labels': {
            'app': name,
            'project': name
            },
            'name': name,
            'namespace': 'default'
          },
          'spec': {
            'containers': [container]
          }
        }
      }
    )
  ])
  return YAML_HEADER + yaml.safe_dump(deployment, default_flow_style=False)

def build_service(name, port, target_port=None, internal=True):
  if target_port is None:
    target_port = port

  spec = {
    'ports': [{'port': port, 'targetPort': target_port, 'protocol': 'TCP'}],
    'selector': {'app': name}
  }

  if internal:
    spec['type'] = 'ClusterIP'
  else:
    spec['type'] = 'LoadBalancer'
    spec['sessionAffinity'] = 'None'

  service = OrderedDict([
    ('apiVersion', 'v1'),
    ('kind', 'Service'),
    ('metadata', {
      'labels': {'app': name},
      'name': name,
      'namespace': 'default'
    }),
    ('spec', spec)
  ])
  return YAML_HEADER + yaml.safe_dump(service, default_flow_style=False)
