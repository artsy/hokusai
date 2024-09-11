import copy
import json

from hokusai.lib.common import delete_keys, shout, write_temp_file
from hokusai.lib.config import HOKUSAI_TMP_DIR
from hokusai.services.kubectl import Kubectl

import pdb

class ServiceAccount:
  ''' represent a Kubernetes ServiceAccount '''

  k8s_dynamic_fields = {
    'metadata': {
      'annotations': {
        'kubectl.kubernetes.io/last-applied-configuration': {}
      },
      'creationTimestamp': {},
      'resourceVersion': {},
      'uid': {}
    },
    'secrets': {}
  }

  def __init__(
      self,
      context,
      namespace='default',
      name=None,
      spec={}

  ):
    self.context = context
    self.kctl = Kubectl(context, namespace=namespace)
    self.name = name

    # if resource exists in Kubernetes,
    # its representation should be stored here.
    # should be in sync with self.spec
    self.object = {}

    # store the spec that can be used
    # to create/update the object in Kubernetes.
    # should be in sync with self.object,
    # if object exists in Kubernetes
    self.spec = spec

  def apply(self):
    ''' apply service account spec to Kubernetes '''
    path = write_temp_file(
      json.dumps(self.spec),
      HOKUSAI_TMP_DIR
    )
    self.kctl.apply(path)
    # should call self.load to update object,
    # but will have to account for delay in Kubernetes apply

  def load(self):
    ''' read object from Kubernetes and store it '''
    payload = shout(
      self.kctl.command(
        f'get serviceaccount {self.name} -o json'
      )
    )
    self.object = json.loads(payload)
    # keep spec in sync
    spec = copy.deepcopy(self.object)
    delete_keys(
      spec,
      self.k8s_dynamic_fields
    )
    self.spec = spec
