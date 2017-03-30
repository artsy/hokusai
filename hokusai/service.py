from hokusai.config import config
from hokusai.common import print_red, print_green, shout, get_ecr_login
from hokusai.kubectl import Kubectl

class Service(object):
  def __init__(self, context):
    self.context = context
    self.kctl = Kubectl(self.context)
    self.cache = self.kctl.get_object('service', selector="app=%s" % config.project_name)

  @property
  def state(self):
    if len(self.cache['items']) != 1:
      print_red("Multiple services found for %s" % config.project_name)
      return None
    return self.cache['items'][0]
