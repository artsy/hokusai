import json
import os

import yaml

from hokusai.lib.common import shout
from hokusai.lib.global_config import HokusaiGlobalConfig


class Kubectl:
  ''' run kubectl commands '''
  def __init__(self, context, namespace=None):
    self.context = context
    self.namespace = namespace
    global_config = HokusaiGlobalConfig()
    self.kubectl = os.path.join(
      global_config.kubectl_dir, 'kubectl'
    )

  def command(self, cmd):
    ''' generate kubectl command '''
    if self.namespace is None:
      return f'{self.kubectl} --context {self.context} {cmd}'
    return (
      f'{self.kubectl} --context {self.context} ' +
      f'--namespace {self.namespace} {cmd}'
    )

  def contexts(self):
    ''' return all k8s contexts found in kubeconfig '''
    return [
      context['name'] for context in
      yaml.load(
        shout(f'{self.kubectl} config view'),
        Loader=yaml.FullLoader
      )['contexts']
    ]

  def get_object(self, obj):
    ''' run kubectl get <object> '''
    cmd = self.command(f'get {obj} -o json)')
    try:
      return json.loads(shout(cmd))
    except ValueError:
      return None

  def get_objects(self, obj, selector=None):
    ''' run kubectl get <object> with selectors '''
    if selector is not None:
      cmd = self.command(
        f'get {obj} --selector {selector} -o json'
      )
    else:
      cmd = self.command(f'get {obj} -o json')
    try:
      return json.loads(shout(cmd))['items']
    except ValueError:
      return []
