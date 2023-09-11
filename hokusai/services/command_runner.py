import copy
import re
import json
import pipes

from hokusai.lib.config import config
from hokusai.lib.common import shout, returncode, k8s_uuid, user, validate_env_var
from hokusai.services.ecr import ECR
from hokusai.services.kubectl import Kubectl
from hokusai.lib.exceptions import HokusaiError

class CommandRunner:
  def __init__(self, context, namespace=None):
    self.context = context
    self.kctl = Kubectl(self.context, namespace=namespace)
    self.ecr = ECR()
    self.pod_name = self._name()
    self.container_name = self._name()

  def _name(self):
    ''' generate name for pod and container '''
    name = '-'.join(
      filter(
        None,
        [
          f"{config.project_name}-hokusai-run",
          user(),
          k8s_uuid()
        ]
      )
    )
    return name

  def _image_name(self, tag_or_digest):
    ''' generate docker image name '''
    separator = "@" if ":" in tag_or_digest else ":"
    image_name = f"{self.ecr.project_repo}{separator}{tag_or_digest}"
    return image_name

  def _append_env(self, container_spec, env):
    ''' append env to given container spec '''
    spec = copy.deepcopy(container_spec)
    spec['env'] = []
    for var in env:
      validate_env_var(var)
      split = var.split('=', 1)
      spec['env'].append(
        {'name': split[0], 'value': split[1]}
      )
    return spec

  def _append_envfrom(self, container_spec):
    ''' append envFrrom to given container spec '''
    spec = copy.deepcopy(container_spec)
    spec.update(
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
    return spec

  def _append_constraint(self, containers_spec, constraint):
    ''' append node constraint to given containers spec '''
    spec = copy.deepcopy(containers_spec)
    constraint = constraint or config.run_constraints
    if constraint:
      spec['nodeSelector'] = {}
      for label in constraint:
        if '=' not in label:
          raise HokusaiError(
            "Error: Node selectors must of the form 'key=value'"
          )
        split = label.split('=', 1)
        spec['nodeSelector'][split[0]] = split[1]
    return spec

  def _overrides_container(self, cmd, env, tag_or_digest):
    ''' generate overrides['spec']['containers'][0] spec '''
    spec = {
      "args": cmd.split(' '),
      "name": self.container_name,
      "image": self._image_name(tag_or_digest),
      "imagePullPolicy": "Always",
    }
    spec = self._append_env(spec, env)
    spec = self._append_envfrom(spec)
    return spec

  def _overrrides_containers(self, cmd, env, tag_or_digest):
    ''' generate overrides['spec']['containers'] spec '''
    container_spec = self._overrides_container(
      cmd, env, tag_or_digest
    )
    spec = { "containers": [container_spec] }
    return containers_spec

  def _overrides_spec(self, cmd, constraint, env, tag_or_digest):
    ''' generate overrides['spec'] spec '''
    spec = {}
    containers_spec = self._overrrides_containers(
      cmd, env, tag_or_digest
    )
    spec.update(containers_spec)
    spec = self._append_constraint(spec, constraint)
    return spec

  def _overrides(self, cmd, constraint, env, tag_or_digest):
    ''' generate overrides '''
    overrides = { "apiVersion": "v1", "spec": spec }
    spec = self._overrides_spec(cmd, constraint, env, tag_or_digest)
    overrides.update(spec)
    return overrides

  def _run_no_tty(self, cmd, image_name, overrides):
    ''' run command without tty '''
    args = ' '.join(
      "run",
      self.pod_name,
      "--attach",
      f"--image={image_name}",
      f"--overrides={pipes.quote(json.dumps(overrides))}",
      "--restart=Never",
      "--rm"
    )
    return returncode(
      self.kctl.command(args)
    )

  def _run_tty(self, cmd, image_name, overrides):
    ''' run command with tty '''
    overrides['spec']['containers'][0].update({
      "stdin": True,
      "stdinOnce": True,
      "tty": True
    })
    args = ' '.join(
      "run",
      self.pod_name,
      "-t",
      "-i",
      f"--image={image_name}",
      "--restart=Never",
      f"--overrides={pipes.quote(json.dumps(overrides))}",
      "--rm"
    )
    shout(
      self.kctl.command(args),
      print_output=True
    )

  def run(self, tag_or_digest, cmd, tty=None, env=(), constraint=()):
    ''' run command '''
    run_tty = tty if tty is not None else config.run_tty
    overrides = self._overrrides(
      cmd, constraint, env, tag_or_digest
    )
    image_name = self._image_name(tag_or_digest)
    if run_tty:
      self._run_tty(cmd, image_name, overrides)
    else:
      self._run_no_tty(cmd, image_name, overrides)
