import copy
import json

from hokusai.lib.common import shout, write_temp_file
from hokusai.lib.config import HOKUSAI_TMP_DIR
from hokusai.services.kubectl import Kubectl


class ServiceAccount:
  ''' represent a Kubernetes ServiceAccount '''
  def __init__(self, context, namespace='default', name=None, spec={}):
    self.context = context
    self.kctl = Kubectl(context, namespace=namespace)
    self.name = name
    self.struct = {}
    self.spec = spec

  def load(self):
    ''' read service account spec from Kubernetes '''
    payload = shout(
      self.kctl.command("get serviceaccount %s -o json" % self.name)
    )
    self.struct = json.loads(payload)

  def clean_spec(self):
    ''' return k8s spec cleaned of dynamic fields '''
    cleaned_spec = copy.deepcopy(self.struct)
    del self.struct['metadata']['annotations']['kubectl.kubernetes.io/last-applied-configuration']
    del self.struct['metadata']['creationTimestamp']
    del self.struct['metadata']['resourceVersion']
    del self.struct['metadata']['uid']
    del self.struct['secrets']
    return cleaned_spec

  def create(self):
    ''' create service account in Kubernetes '''
    path = write_temp_file(
      json.dumps(self.spec), HOKUSAI_TMP_DIR
    )
    self.kctl.create(path)
