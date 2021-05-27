import os
import sys

from tempfile import NamedTemporaryFile

import json

from hokusai.lib.config import config, HOKUSAI_TMP_DIR
from hokusai.lib.common import print_green, shout
from hokusai.services.kubectl import Kubectl
from hokusai.lib.exceptions import HokusaiError

class ConfigMap(object):
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

  def _to_file(self):
    f = NamedTemporaryFile(delete=False, dir=HOKUSAI_TMP_DIR, mode='w')
    f.write(json.dumps(self.struct))
    f.close()
    return f

  def create(self):
    f = self._to_file()
    try:
      shout(self.kctl.command("create -f %s" % f.name))
    finally:
      os.unlink(f.name)

  def destroy(self):
    shout(self.kctl.command("delete configmap %s" % self.name))

  def load(self):
    payload = shout(self.kctl.command("get configmap %s -o json" % self.name))
    struct = json.loads(payload)
    if 'data' in struct:
      self.struct['data'] = struct['data']
    else:
      self.struct['data'] = {}

  def save(self):
    f = self._to_file()
    try:
      shout(self.kctl.command("apply -f %s" % f.name))
    finally:
      os.unlink(f.name)

  def all(self):
    return self.struct['data']

  def update(self, key, value):
    self.struct['data'].update({key: value})

  def delete(self, key):
    try:
      del self.struct['data'][key]
    except KeyError:
      raise HokusaiError("Cannot unset '%s' as it does not exist" % key)
