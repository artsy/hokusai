import os
import re
import json
import pipes

from hokusai.lib.config import config
from hokusai.lib.common import shout, returncode, k8s_uuid
from hokusai.services.ecr import ECR
from hokusai.services.kubectl import Kubectl
from hokusai.lib.exceptions import HokusaiError

class CommandRunner:
  def __init__(self, context, namespace=None):
    self.context = context
    self.kctl = Kubectl(self.context, namespace=namespace)
    self.ecr = ECR()

  def check_env(env):
    container['env'] = []
    for s in env:
      if '=' not in s:
        raise HokusaiError("Error: environment variables must be of the form 'KEY=VALUE'")
      split = s.split('=', 1)
      container['env'].append({'name': split[0], 'value': split[1]})

  def create_overrides(self):
    ''' compile overrides spec for kubectl run '''
    container = {
      "args": cmd.split(' '),
      "name": name,
      "image": image_name,
      "imagePullPolicy": "Always",
      'envFrom': [
        {
          'configMapRef': {
            'name': f'{config.project_name}-environment'
          }
        },
        {
          'secretRef': {
            'name': f'{config.project_name}',
            'optional': True
          }
        }
      ]
    }
    spec = { "containers": [container] }
    constraints = constraint or config.run_constraints
    if constraints:
      spec['nodeSelector'] = {}
      for label in constraints:
        if '=' not in label:
          raise HokusaiError("Error: Node selectors must of the form 'key=value'")
        split = label.split('=', 1)
        spec['nodeSelector'][split[0]] = split[1]
    overrides = { "apiVersion": "v1", "spec": spec }

  def container_name():
    if os.environ.get('USER') is not None:
      # The regex used for the validation of name is '[a-z0-9]([-a-z0-9]*[a-z0-9])?'
      user = re.sub("[^0-9a-z]+", "-", os.environ.get('USER').lower())
      uuid = "%s-%s" % (user, k8s_uuid())
    else:
      uuid = k8s_uuid()
    name = "%s-hokusai-run-%s" % (config.project_name, uuid)
    separator = "@" if ":" in tag_or_digest else ":"

  def image_name():
    image_name = "%s%s%s" % (self.ecr.project_repo, separator, tag_or_digest)

  def run_tty(overrides):
    container.update({
      "stdin": True,
      "stdinOnce": True,
      "tty": True
    })
    shout(self.kctl.command("run %s -t -i --image=%s --restart=Never --overrides=%s --rm" %
                   (name, image_name, pipes.quote(json.dumps(overrides)))), print_output=True)

  def run_no_tty(overrides):
    return returncode(self.kctl.command("run %s --attach --image=%s --overrides=%s --restart=Never --rm" %
                                      (name, image_name, pipes.quote(json.dumps(overrides)))))

  def run(self, tag_or_digest, cmd, tty=None, env=(), constraint=()):
    run_tty = tty if tty is not None else config.run_tty
    overrides = self.creat_overrrides()
    if run_tty:
      self.run_tty(overrides)
    else run_no_tty():
      self.run_no_tty(overrides):
