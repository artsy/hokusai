import os
import sys

from collections import OrderedDict
from tempfile import NamedTemporaryFile

import yaml

from hokusai.lib.config import config
from hokusai.lib.common import print_red, print_green, shout
from hokusai.services.kubectl import Kubectl

class ConfigMap(object):
  def __init__(self, context):
    self.context = context
    self.kctl = Kubectl(context)
    self.struct = OrderedDict([
      ('apiVersion', 'v1'),
      ('kind', 'ConfigMap'),
      ('metadata', {
        'labels': {'app': config.project_name},
        'name': "%s-environment" % config.project_name
      }),
      ('data', {})
    ])

  def _to_file(self):
    f = NamedTemporaryFile(delete=False)
    f.write(yaml.safe_dump(self.struct, default_flow_style=False))
    f.close()
    return f.name

  def create(self):
    f = self._to_file()
    try:
      shout(self.kctl.command("create -f %s" % f))
    finally:
      os.unlink(f)

  def destroy(self):
    shout(self.kctl.command("delete configmap %s-environment" % config.project_name))

  def load(self):
    payload = shout(self.kctl.command("get configmap %s-environment -o yaml" % config.project_name))
    struct = yaml.load(payload)
    if 'data' in struct:
      self.struct['data'] = struct['data']
    else:
      self.struct['data'] = {}

  def save(self):
    f = self._to_file()
    try:
      shout(self.kctl.command("apply -f %s" % f))
    finally:
      os.unlink(f)

  def all(self):
    for k, v in self.struct['data'].iteritems():
      yield k, v

  def update(self, key, value):
    self.struct['data'].update({key: value})

  def delete(self, key):
    try:
      del self.struct['data'][key]
    except KeyError:
      print_red("Cannot unset '%s' as it does not exist" % key)
