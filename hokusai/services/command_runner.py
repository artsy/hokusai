import copy
import json
import os
import pipes
import re

from hokusai import CWD
from hokusai.lib.common import (
  file_debug,
  k8s_uuid,
  returncode,
  shout,
  user,
  validate_key_value
)
from hokusai.lib.config import (
  config,
  HOKUSAI_CONFIG_DIR
)
from hokusai.lib.exceptions import HokusaiError
from hokusai.lib.template_selector import TemplateSelector
from hokusai.services.ecr import ECR
from hokusai.services.kubectl import Kubectl
from hokusai.services.yaml_spec import YamlSpec


class CommandRunner:
  def __init__(self, context, namespace=None):
    self.context = context
    self.kctl = Kubectl(self.context, namespace=namespace)
    self.ecr = ECR()
    self.pod_name = self._name()
    self.container_name = self.pod_name
    self.yaml_template = TemplateSelector().get(
      os.path.join(CWD, HOKUSAI_CONFIG_DIR, context)
    )
    if not config.run_template:
      raise HokusaiError(
        'run-template config must be specified in Hokusai config file'
      )
    self.model_deployment = config.run_template
    self.secrets_file = config.secrets_file

  def _clean_containers_spec(self, spec):
    '''
    given a pod's 'containers' spec, return that spec,
    but ensure that each container spec has only the desired fields.
    '''
    container_fields_to_keep = [
      'args',
      'envFrom',
      'image',
      'imagePullPolicy',
      'name',
      'volumeMounts'
    ]
    clean_spec = []
    for container_spec in spec:
      clean_spec += [
        self._clean_resource_spec(container_spec, container_fields_to_keep)
      ]
    return clean_spec

  def _clean_pod_spec(self, spec):
    '''
    given a pod spec, return that spec,
    but ensure that it has only the desired fields.
    '''
    pod_fields_to_keep = [
      'containers',
      'dnsConfig',
      'dnsPolicy',
      'initContainers',
      'serviceAccountName',
      'volumes'
    ]
    clean_spec = self._clean_resource_spec(
      spec, pod_fields_to_keep
    )
    file_debug(
      clean_spec,
      file_suffix='command_runner._clean_pod_spec.clean_spec'
    )
    clean_spec['containers'] = self._clean_containers_spec(
      clean_spec['containers']
    )
    return clean_spec

  def _clean_resource_spec(self, spec, fields_to_keep):
    ''' return spec ensuring that it contains only desired fields '''
    clean_spec = {
      field: spec[field]
      for field in fields_to_keep
      if field in spec
    }
    return clean_spec

  def _finalize_cmd(self, cmd):
    ''' return the cmd that is to be run by kubectl '''
    if self.secrets_file:
      return [
        'sh',
        '-c',
        f'source {self.secrets_file} ' + '&& ' + cmd
      ]
    else:
      return cmd.split(' ')

  def _name(self):
    ''' fabricate a name for the pod and container '''
    name = '-'.join(
      filter(
        None,
        [
          f'{config.project_name}-hokusai-run',
          user(),
          k8s_uuid()
        ]
      )
    )
    return name

  def _image_name(self, tag_or_digest):
    ''' compose name for the docker image field in pod spec '''
    separator = '@' if ':' in tag_or_digest else ':'
    image_name = f'{self.ecr.project_repo}{separator}{tag_or_digest}'
    return image_name

  def _overrides(self, cmd, constraint, env, tag_or_digest, pod_spec):
    ''' create overrides spec for kubectl '''
    overrides = { 'apiVersion': 'v1', 'spec': pod_spec}
    overrides['spec']['containers'][0]['args'] = self._finalize_cmd(cmd)
    overrides['spec']['containers'][0]['name'] = self.container_name
    overrides['spec']['containers'][0]['image'] = self._image_name(
      tag_or_digest
    )
    constraint = constraint or config.run_constraints
    if constraint:
      overrides['spec']['nodeSelector'] = {}
      for label in constraint:
        validate_key_value(label)
        split = label.split('=', 1)
        overrides['spec']['nodeSelector'][split[0]] = split[1]
    if env:
      overrides['spec']['containers'][0]['env'] = []
      for var in env:
        validate_key_value(var)
        split = var.split('=', 1)
        overrides['spec']['containers'][0]['env'].append(
          {'name': split[0], 'value': split[1]}
        )
    return overrides

  def _run_no_tty(self, cmd, image_name, overrides):
    ''' run command without tty '''
    args = ' '.join(
      [
        'run',
        self.pod_name,
        '--attach',
        f'--image={image_name}',
        f'--overrides={pipes.quote(json.dumps(overrides))}',
        '--restart=Never',
        '--rm'
      ]
    )
    file_debug(
      overrides,
      file_suffix='command_runner.run_no_tty.overrides'
    )
    return returncode(
      self.kctl.command(args)
    )

  def _run_tty(self, cmd, image_name, overrides):
    ''' run command with tty '''
    overrides['spec']['containers'][0].update({
      'stdin': True,
      'stdinOnce': True,
      'tty': True
    })
    args = ' '.join(
      [
        'run',
        self.pod_name,
        '-t',
        '-i',
        f'--image={image_name}',
        '--restart=Never',
        f'--overrides={pipes.quote(json.dumps(overrides))}',
        '--rm'
      ]
    )
    file_debug(
      overrides,
      file_suffix='command_runner.run_tty.overrides'
    )
    shout(
      self.kctl.command(args),
      print_output=True
    )

  def run(self, tag_or_digest, cmd, tty=None, env=(), constraint=()):
    '''
    spawn a pod to run the specified command,
    create an overrides spec to be given to kubectl run,
    base the override on:
    - pod spec of a model deployment spec in the appropriate hokusai yaml
    - the args to this function
    '''
    pod_spec = YamlSpec(
      self.yaml_template,
      render_template=True
    ).extract_pod_spec(self.model_deployment)
    file_debug(
      pod_spec,
      file_suffix='command_runner.run.pod_spec'
    )
    # clean specs so they are appropriate for kubectl run
    clean_pod_spec = self._clean_pod_spec(pod_spec)
    run_tty = tty if tty is not None else config.run_tty
    overrides = self._overrides(
      cmd,
      constraint,
      env,
      tag_or_digest,
      clean_pod_spec
    )
    image_name = self._image_name(tag_or_digest)
    if run_tty:
      self._run_tty(cmd, image_name, overrides)
    else:
      return self._run_no_tty(cmd, image_name, overrides)
