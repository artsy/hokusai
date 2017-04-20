import json

import yaml

from hokusai.lib.common import shout

class Kubectl(object):
  def __init__(self, context):
    self.context = context

  def command(self, cmd):
    return "kubectl --context %s %s" % (self.context, cmd)

  def get_object(self, obj, selector=None):
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
