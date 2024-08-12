import copy
import json
import os
import pipes
import re

from tempfile import NamedTemporaryFile

from hokusai import CWD
from hokusai.lib.common import (
  k8s_uuid, returncode, shout, user, validate_key_value, filter_dict
)
from hokusai.lib.config import config, HOKUSAI_CONFIG_DIR, HOKUSAI_TMP_DIR
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

  def _debug(self, overrides, suffix=None):
    ''' dump overrides into a file for debug '''
    if os.environ.get('DEBUG'):
      with NamedTemporaryFile(delete=False, dir=HOKUSAI_TMP_DIR, mode='w', suffix=suffix) as temp_file:
        pretty_json = json.dumps(overrides, indent=2)
        temp_file.write(pretty_json)

  def _name(self):
    ''' generate name for pod and container '''
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
    ''' generate docker image name '''
    separator = '@' if ':' in tag_or_digest else ':'
    image_name = f'{self.ecr.project_repo}{separator}{tag_or_digest}'
    return image_name

  def _overrides(self, cmd, constraint, env, tag_or_digest, pod_spec):
    ''' generate overrides '''
    overrides = { 'apiVersion': 'v1', 'spec': pod_spec}
    # assume 1) there's a secrets file, 2) the path to it
    secrets_file = '/secrets/secrets'
    overrides['spec']['containers'][0]['args'] = [
      'sh',
      '-c',
      'source /secrets/secrets ' + '&& ' + cmd
    ]
    overrides['spec']['containers'][0]['name'] = self.container_name
    overrides['spec']['containers'][0]['image'] = self._image_name(tag_or_digest)
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
    self._debug(overrides, suffix='command_runner.run_no_tty')
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
    self._debug(overrides, suffix='command_runner.run_tty')
    shout(
      self.kctl.command(args),
      print_output=True
    )

  def run(self, tag_or_digest, cmd, tty=None, env=(), constraint=()):
    ''' run command '''
    # assume we want to use <project>-web deployment as template
    template_deployment = config.project_name + '-web'
    yaml_template = TemplateSelector().get(os.path.join(CWD, HOKUSAI_CONFIG_DIR, self.context))
    run_template = YamlSpec(yaml_template, render_template=True).extract_pod_spec(template_deployment)

    self._debug(run_template, suffix='command_runner.run.run_template')

    # ensure pod_spec contains only fields appropriate for run
    fields_to_keep = [
      'initContainers',
      'containers',
      'dnsPolicy',
      'dnsConfig',
      'serviceAccountName',
      'volumes'
    ]
    cleaned_pod_spec = filter_dict(run_template, fields_to_keep)
    self._debug(cleaned_pod_spec, suffix='command_runner.run.cleaned_pod_spec')

    # ensure containers spec contains only fields appropriate for run
    fields_to_keep = [
      'name',
      'envFrom',
      'args',
      'image',
      'imagePullPolicy',
      'volumeMounts'
    ]
    cleaned_containers_spec = []
    for container_spec in cleaned_pod_spec['containers']:
      cleaned_containers_spec += [filter_dict(container_spec, fields_to_keep)]
    cleaned_pod_spec['containers'] = cleaned_containers_spec

    run_tty = tty if tty is not None else config.run_tty
    overrides = self._overrides(
      cmd, constraint, env, tag_or_digest, cleaned_pod_spec
    )
    image_name = self._image_name(tag_or_digest)
    if run_tty:
      self._run_tty(cmd, image_name, overrides)
    else:
      return self._run_no_tty(cmd, image_name, overrides)
