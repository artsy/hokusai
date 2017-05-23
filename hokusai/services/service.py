from hokusai.lib.config import config
from hokusai.services.kubectl import Kubectl

class Service(object):
  def __init__(self, context, application_only=True):
    self.context = context
    self.kctl = Kubectl(self.context)

    if application_only:
      selector = "app=%s,layer=application" % config.project_name
    else:
      selector = "app=%s" % config.project_name

    self.cache = self.kctl.get_object('service', selector=selector)
