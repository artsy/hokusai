import os

import json

from tempfile import NamedTemporaryFile

from hokusai.lib.common import shout
from hokusai.lib.config import HOKUSAI_TMP_DIR
from hokusai.lib.exceptions import HokusaiError
from hokusai.services.kubectl import Kubectl


class Namespace:
  ''' represent a Kubernetes namespace '''
  def __init__(self, context, name, labels=None):
    self.context = context
    self.kctl = Kubectl(context)
    self.name = name
    self.labels = labels
    self.struct = {}

  def delete(self):
    ''' delete namespace '''
    if self.name == 'default':
      raise HokusaiError(f'Cannot delete "default" namespace.')
    shout(self.kctl.command(f'delete namespace {self.name}'))

  def _to_file(self):
    ''' return object of temp file containing struct '''
    temp_file_obj = NamedTemporaryFile(delete=False, dir=HOKUSAI_TMP_DIR, mode='w')
    temp_file_obj.write(json.dumps(self.struct))
    temp_file_obj.close()
    return temp_file_obj

  def create(self):
    ''' create namespace '''
    if self.name == 'default':
      raise HokusaiError(f'Cannot create "default" namespace.')
    metadata = {
      'name': self.name,
      'labels': self.labels
    }
    self.struct = {
      'apiVersion': 'v1',
      'kind': 'Namespace',
      'metadata': metadata
    }
    file_obj = self._to_file()
    try:
      shout(self.kctl.command(f'create -f {file_obj.name}'))
    finally:
      os.unlink(file_obj.name)
