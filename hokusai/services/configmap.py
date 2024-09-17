import os
import sys

import json

from hokusai.lib.common import shout, write_temp_file
from hokusai.lib.config import config, HOKUSAI_TMP_DIR
from hokusai.lib.exceptions import HokusaiError
from hokusai.services.kubectl import Kubectl


class ConfigMap:
  ''' represent a Kubernetes ConfigMap '''
  def __init__(self, context, namespace='default', name=None):
    self.context = context
    self.kctl = Kubectl(context, namespace=namespace)
    self.name = name or f'{config.project_name}-environment'
    self.metadata = {
      'name': self.name,
      'namespace': namespace
    }
    if name is None:
      self.metadata['labels'] = {
        'app': config.project_name
      }
    self.struct = {
      'apiVersion': 'v1',
      'kind': 'ConfigMap',
      'metadata': self.metadata,
      'data': {}
    }

  def all(self):
    ''' return configmap data '''
    return self.struct['data']

  def create(self):
    ''' create configmap in Kubernetes '''
    path = write_temp_file(
      json.dumps(self.struct), HOKUSAI_TMP_DIR
    )
    self.kctl.create(path)

  def delete(self, key):
    ''' delete one key in configmap '''
    try:
      del self.struct['data'][key]
    except KeyError:
      raise HokusaiError(
        "Cannot unset '%s' as it does not exist" % key
      )

  def destroy(self):
    ''' delete configmap in Kubernetes '''
    shout(
      self.kctl.command("delete configmap %s" % self.name),
      print_output=True
    )

  def load(self):
    ''' read configmap data from Kubernetes '''
    payload = shout(
      self.kctl.command("get configmap %s -o json" % self.name)
    )
    struct = json.loads(payload)
    struct['data'] = struct.setdefault('data', {})
    self.struct['data'] = struct['data']

  def save(self):
    ''' save changes to Kubernetes '''
    path = write_temp_file(
      json.dumps(self.struct), HOKUSAI_TMP_DIR
    )
    self.kctl.apply(path)

  def update(self, key, value):
    ''' update value of a key in configmap '''
    self.struct['data'].update({key: value})
