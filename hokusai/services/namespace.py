import os

import json

from hokusai.lib.common import shout, write_temp_file
from hokusai.lib.config import HOKUSAI_TMP_DIR
from hokusai.lib.exceptions import HokusaiError
from hokusai.services.kubectl import Kubectl


class Namespace:
  ''' represent a Kubernetes namespace '''
  def __init__(self, context, name, labels={}):
    self.context = context
    self.kctl = Kubectl(context)
    self.name = name
    self.labels = labels
    self.struct = {}

  def create(self):
    ''' create namespace '''
    if self.name == 'default':
      raise HokusaiError(
        f'Cannot create "default" namespace.'
      )
    metadata = {
      'name': self.name,
      'labels': self.labels
    }
    self.struct = {
      'apiVersion': 'v1',
      'kind': 'Namespace',
      'metadata': metadata
    }
    path = write_temp_file(
      json.dumps(self.struct), HOKUSAI_TMP_DIR
    )
    self.kctl.apply(path)

  def delete(self):
    ''' delete namespace '''
    if self.name == 'default':
      raise HokusaiError(f'Cannot delete "default" namespace.')
    shout(self.kctl.command(f'delete namespace {self.name}'))
