import os

import json
import yaml

from hokusai.lib.common import shout, unlink_file_if_not_debug
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

  def _apply_or_create(self, action, k8s_spec_file):
    ''' run kubectl apply or create on a k8s spec file '''
    try:
      shout(
        self.command(f'{action} -f {k8s_spec_file}'),
        print_output=True
      )
    finally:
      unlink_file_if_not_debug(k8s_spec_file)

  def apply(self, k8s_spec_file):
    ''' run kubectl apply on a k8s spec file '''
    self._apply_or_create('apply', k8s_spec_file)

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

  def create(self, k8s_spec_file):
    ''' run kubectl create on a k8s spec file '''
    self._apply_or_create('create', k8s_spec_file)

  def get_object(self, obj):
    ''' run kubectl get <object> '''
    cmd = self.command(f'get {obj} -o json')
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
