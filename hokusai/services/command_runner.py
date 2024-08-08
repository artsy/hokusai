import copy
import json
import os
import pipes
import re

from tempfile import NamedTemporaryFile

from hokusai import CWD
from hokusai.lib.common import (
  k8s_uuid, returncode, shout, user, validate_key_value
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
    overrides['spec']['containers'][0]['args'] = cmd.split(' ')
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

  def _get_deployment_spec(self, deployment_name):
    ''' return spec of specified deployment, from proper hokusai yaml '''
    deployment_spec = None
    yaml_template = TemplateSelector().get(os.path.join(CWD, HOKUSAI_CONFIG_DIR, self.context))
    yaml_spec = YamlSpec(yaml_template, render_template=True).to_list()
    for item in yaml_spec:
      if item['kind'] == 'Deployment' and item['metadata']['name'] == deployment_name:
        deployment_spec = item
    if not deployment_spec:
      raise HokusaiError(f'Failed to find {deployment_name} deployment in {yaml_template}')
    return deployment_spec

  def _extract_pod_spec(self, deployment_name):
    ''' get pod spec from specified deployment, from proper hokusai yaml '''
    pod_spec = None
    deployment_spec = self._get_deployment_spec(deployment_name)
    pod_spec = deployment_spec['spec']['template']['spec']
    if not pod_spec:
      raise HokusaiError(f'Failed to find pod spec in {deployment_name} deployment spec')
    return pod_spec

  def _clean_pod_spec(self, pod_spec):
    ''' return subset of fields in pod spec that are appropriate for kubectl run '''
    cleaned_spec = {}
    fields_to_keep = [
      'initContainers',
      'containers',
      'dnsPolicy',
      'dnsConfig',
      'serviceAccountName',
      'volumes'
    ]
    for field in fields_to_keep:
      if field in pod_spec:
        field_spec = pod_spec[field]
        if field == 'containers':
          field_spec = self._clean_containers_spec(field_spec)
        cleaned_spec.update({field: field_spec})
    return cleaned_spec

  def _clean_containers_spec(self, containers_spec):
    ''' return subset of fields in pod containers spec that are appropriate for kubectl run '''
    cleaned_spec = []
    fields_to_keep = [
      'name',
      'envFrom',
      'args',
      'image',
      'imagePullPolicy',
      'volumeMounts'
    ]
    for container_spec in containers_spec:
      cleaned_container_spec = {}
      for field in fields_to_keep:
        if field in container_spec:
          field_spec = container_spec[field]
          cleaned_container_spec.update({field: field_spec})
      cleaned_spec = cleaned_spec + [cleaned_container_spec]
    return cleaned_spec

  def run(self, tag_or_digest, cmd, tty=None, env=(), constraint=()):
    ''' run command '''
    # assume we want to use <project>-web deployment as template
    template_deployment = config.project_name + '-web'
    run_template = self._extract_pod_spec(template_deployment)
    self._debug(run_template, suffix='command_runner.run.run_template')

    # ensure pod_spec contains only fields appropriate for run
    cleaned_pod_spec = self._clean_pod_spec(run_template)
    self._debug(cleaned_pod_spec, suffix='command_runner.run.cleaned_pod_spec')

    run_tty = tty if tty is not None else config.run_tty
    overrides = self._overrides(
      cmd, constraint, env, tag_or_digest, cleaned_pod_spec
    )
    image_name = self._image_name(tag_or_digest)
    if run_tty:
      self._run_tty(cmd, image_name, overrides)
    else:
      return self._run_no_tty(cmd, image_name, overrides)
