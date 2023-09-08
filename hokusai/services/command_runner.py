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

  def _name(self):
    ''' generate container name '''
    if os.environ.get('USER') is not None:
      # The regex used for the validation of name is
      # '[a-z0-9]([-a-z0-9]*[a-z0-9])?'
      user = re.sub(
        "[^0-9a-z]+", "-", os.environ.get('USER').lower()
      )
      uuid = "{user}-{k8s_uuid()}"
    else:
      uuid = k8s_uuid()
    name = "{config.project_name}-hokusai-run-{uuid}"
    return name

  def _image_name(self, tag_or_digest):
    ''' generate docker image name '''
    separator = "@" if ":" in tag_or_digest else ":"
    image_name = f"{self.ecr.project_repo}{separator}{tag_or_digest}"
    return image_name

  def _validate_env(self, kv):
    ''' ensure kv is in KEY=VALUE form '''
    if '=' not in s:
      raise HokusaiError(
        "Error: environment variables must be of the form 'KEY=VALUE'"
      )

  def _append_env(self, container_spec, env):
    ''' append env to given container spec '''
    container_spec['env'] = []
    for kv in env:
      self._validate_env(kv)
      split = kv.split('=', 1)
      container_spec['env'].append(
        {'name': split[0], 'value': split[1]}
      )

  def _append_envfrom(container_spec):
    ''' append envFrrom to given container spec '''
    container_spec = container_spec.update(
      {
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
    )

  def _append_constraints(containers_spec, constraint):
    ''' append constraints to given containers spec '''
    constraints = constraint or config.run_constraints
    if constraints:
      containers_spec['nodeSelector'] = {}
      for label in constraints:
        if '=' not in label:
          raise HokusaiError(
            "Error: Node selectors must of the form 'key=value'"
          )
        split = label.split('=', 1)
        containters_spec['nodeSelector'][split[0]] = split[1]
    return containers_spec

  def _overrides_spec_containers_container(self, cmd, env, tag_or_digest):
    ''' generate container spec '''
    container_spec = {
      "args": cmd.split(' '),
      "name": self.container_name(),
      "image": self._image_name(tag_or_digest),
      "imagePullPolicy": "Always",
    }
    container = self._append_env(container_spec, env)
    container = self._append_envfrom(container_spec)
    return container_spec

  def _overrrides_spec_containers(self, cmd, env, tag_or_digest):
    ''' generate containers spec '''
    containers_spec = {}
    container_spec = self._overrides_spec_containers_container(
      cmd, env, tag_or_digest
    )
    containers_spec = { "containers": [container_spec] }
    return containers_spec

  def _overrides_spec(self, cmd, env, tag_or_digest, constraint):
    ''' generate spec spec '''
    spec = {}
    containers_spec = self._overrrides_spec_containers(
      cmd, env, tag_or_digest
    )
    spec.update(containers_spec)
    spec = self._append_constraints(spec, constraint)
    return spec

  def _overrides(self, cmd, env, tag_or_digest, constraint):
    ''' generate overrides spec '''
    overrides = { "apiVersion": "v1", "spec": spec }
    spec = self._overrides_spec(cmd, env, tag_or_digest_constraint)
    overrides.update(spec)
    return overrides

  def _run_tty(tag_or_digest, overrides):
    ''' run command with tty '''
    overrides['spec']['containers'][0].update({
      "stdin": True,
      "stdinOnce": True,
      "tty": True
    })
    name = self._name()
    image_name = self._image_name(tag_or_digest)
    shout(
      self.kctl.command(
        f"run {name} -t -i --image={image_name} --restart=Never " +
        f"--overrides={pipes.quote(json.dumps(overrides))} --rm"
      ),
      print_output=True
    )

  def _run_no_tty(tag_or_digest, overrides):
    ''' run command without tty '''
    name = self._name()
    image_name = self._image_name(tag_or_digest)
    return returncode(
      self.kctl.command(
        f"run {self._name()} --attach --image={image_name} " +
        f"--overrides={pipes.quote(json.dumps(overrides))} " +
        f"--restart=Never --rm"
      )
    )

  def run(self, tag_or_digest, cmd, tty=None, env=(), constraint=()):
    ''' run command '''
    run_tty = tty if tty is not None else config.run_tty
    overrides = self._overrrides(
      cmd, env, tag_or_digest, constraint
    )
    if run_tty:
      self._run_tty(tag_or_digest, overrides)
    else:
      self._run_no_tty(tag_or_digest, overrides)
