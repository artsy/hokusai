import os
import sys

import json

from hokusai.lib.config import config, HOKUSAI_TMP_DIR
from hokusai.lib.common import print_green, shout write_temp_file
from hokusai.lib.exceptions import HokusaiError
from hokusai.services.kubectl import Kubectl


class ConfigMap:
  ''' represent a Kubernetes ConfigMap '''
  def __init__(self, context, namespace='default', name=None):
    self.context = context
    self.kctl = Kubectl(context, namespace=namespace)
    self.name = name or "%s-environment" % config.project_name
    self.metadata = {
      'name': self.name,
      'namespace': namespace
    }
    if name is None:
      self.metadata['labels'] = { 'app': config.project_name }
    self.struct = {
      'apiVersion': 'v1',
      'kind': 'ConfigMap',
      'metadata': self.metadata,
      'data': {}
    }

  def create(self):
    ''' create configmap '''
    file_obj = write_temp_file(json.dumps(self.struct), HOKUSAI_TMP_DIR)
    self.kctl.create(file_obj.name)

  def destroy(self):
    ''' delete configmap '''
    shout(self.kctl.command("delete configmap %s" % self.name))

  def load(self):
    ''' read configmap into struct '''
    payload = shout(self.kctl.command("get configmap %s -o json" % self.name))
    struct = json.loads(payload)
    if 'data' in struct:
      self.struct['data'] = struct['data']
    else:
      self.struct['data'] = {}

  def save(self):
    ''' save changes to configmap '''
    file_obj = write_temp_file(json.dumps(self.struct), HOKUSAI_TMP_DIR)
    self.kctl.apply(file_obj.name)

  def all(self):
    ''' load configmap data '''
    return self.struct['data']

  def update(self, key, value):
    ''' update value of a key in configmap '''
    self.struct['data'].update({key: value})

  def delete(self, key):
    ''' delete one key in configmap '''
    try:
      del self.struct['data'][key]
    except KeyError:
      raise HokusaiError("Cannot unset '%s' as it does not exist" % key)
