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

def build_deployment(name, image, target_port, layer='application', component='web', environment=None, always_pull=False, replicas=1):
  container = {
    'name': "%s-%s" % (name, component),
    'image': image,
    'ports': [{'containerPort': target_port}]
  }

  if layer == 'application':
    container['envFrom'] = [{'configMapRef': {'name': "%s-environment" % name}}]

  if environment is not None:
    container['env'] = environment

  if always_pull:
    container['imagePullPolicy'] = 'Always'

  deployment = OrderedDict([
    ('apiVersion', 'extensions/v1beta1'),
    ('kind', 'Deployment'),
    ('metadata', {'name': "%s-%s" % (name, component)}),
    ('spec', {
      'replicas': replicas,
      'strategy': {
        'rollingUpdate': {
          'maxSurge': 1,
          'maxUnavailable': 0
        },
        'type': 'RollingUpdate'
      },
      'template': {
        'metadata': {
          'labels': {
            'app': name,
            'layer': layer,
            'component': component
            },
            'name': "%s-%s" % (name, component),
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

def build_service(name, port, layer='application', component='web', target_port=None, internal=True):
  if target_port is None:
    target_port = port

  spec = {
    'ports': [{'port': port, 'targetPort': target_port, 'protocol': 'TCP'}],
    'selector': {
      'app': name,
      'layer': layer,
      'component': component
    }
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
      'labels': {
        'app': name,
        'layer': layer,
        'component': component
      },
      'name': "%s-%s" % (name, component),
      'namespace': 'default'
    }),
    ('spec', spec)
  ])
  return YAML_HEADER + yaml.safe_dump(service, default_flow_style=False)
