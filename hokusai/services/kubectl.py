import json
import os

import yaml

from hokusai.lib.common import shout
from hokusai.lib.global_config import HokusaiGlobalConfig


global_config = HokusaiGlobalConfig()

class Kubectl:
  def __init__(self, context, namespace=None):
    self.context = context
    self.namespace = namespace
    self.kubectl = os.path.join(global_config.kubectl_dir, 'kubectl')

  def command(self, cmd):
    if self.namespace is None:
      return "%s --context %s %s" % (self.kubectl, self.context, cmd)
    return "%s --context %s --namespace %s %s" % (self.kubectl, self.context, self.namespace, cmd)

  def get_object(self, obj):
    cmd = self.command("get %s -o json" % obj)
    try:
      return json.loads(shout(cmd))
    except ValueError:
      return None

  def get_objects(self, obj, selector=None):
    if selector is not None:
      cmd = self.command("get %s --selector %s -o json" % (obj, selector))
    else:
      cmd = self.command("get %s -o json" % obj)
    try:
      return json.loads(shout(cmd))['items']
    except ValueError:
      return []

  def contexts(self):
    return [context['name'] for context in yaml.load(shout('%s config view', self.kubectl), Loader=yaml.FullLoader)['contexts']]
