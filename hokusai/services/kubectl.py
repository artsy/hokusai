import json

import yaml

from hokusai.lib.common import shout

class Kubectl(object):
  def __init__(self, context, namespace=None):
    self.context = context
    self.namespace = namespace

  def command(self, cmd):
    if self.namespace is None:
      return "kubectl --context %s %s" % (self.context, cmd)
    return "kubectl --context %s --namespace %s %s" % (self.context, self.namespace, cmd)

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
    return [context['name'] for context in yaml.load(shout('kubectl config view'))['contexts']]
