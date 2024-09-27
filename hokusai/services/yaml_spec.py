import os

import atexit
import yaml

from botocore.exceptions import NoCredentialsError

from hokusai.lib.common import (
  print_yellow,
  sorted_unique_list,
  unlink_file_if_not_debug,
  write_temp_file
)
from hokusai.lib.config import config, HOKUSAI_TMP_DIR
from hokusai.lib.config_loader import ConfigLoader
from hokusai.lib.exceptions import HokusaiError
from hokusai.lib.template_renderer import TemplateRenderer
from hokusai.services.ecr import ECR


class YamlSpec:
  ''' manage Hokusai yaml template '''
  def __init__(self, template_file, render_template=True):
    self.template_file = template_file
    self.ecr = ECR()
    self.tmp_filename = None
    self.render_template = render_template
    atexit.register(self.cleanup)

  def all_deployments_configmap_refs(self):
    ''' return list of unique configmaps referenced in deployments '''
    configmap_refs = []
    deployment_specs = self.get_resources_by_kind('Deployment')
    for spec in deployment_specs:
      configmap_refs += self.deployment_configmap_refs(spec)
    return sorted_unique_list(configmap_refs)

  def all_deployments_sa_refs(self):
    ''' return list of unique service accounts referenced in deployments '''
    sa_refs = []
    deployment_specs = self.get_resources_by_kind('Deployment')
    for spec in deployment_specs:
      sa_ref = self.deployment_sa_ref(spec)
      if sa_ref is not None:
        sa_refs += [sa_ref]
    return sorted_unique_list(sa_refs)

  def cleanup(self):
    unlink_file_if_not_debug(self.tmp_filename)

  def deployment_sa_ref(self, deployment_spec):
    ''' return any service account referenced in deployment spec '''
    pod_spec = deployment_spec['spec']['template']['spec']
    if 'serviceAccountName' in pod_spec:
      return pod_spec['serviceAccountName']
    else:
      return None

  def deployment_configmap_refs(self, deployment_spec):
    ''' return list of unique configmaps referenced in a deployment '''
    configmap_refs = []
    pod_spec = deployment_spec['spec']['template']['spec']
    if 'initContainers' in pod_spec:
      init_container_specs = pod_spec['initContainers']
      configmap_refs += self.containers_configmap_refs(init_container_specs)
    if 'containers' in pod_spec:
      container_specs = pod_spec['containers']
      configmap_refs += self.containers_configmap_refs(container_specs)
    return sorted_unique_list(configmap_refs)

  def containers_configmap_refs(self, container_specs):
    ''' return list of unique configmaps referenced in container specs '''
    configmap_refs = []
    for spec in container_specs:
      configmap_refs += self.container_configmap_refs(spec)
    return sorted_unique_list(configmap_refs)

  def container_configmap_refs(self, container_spec):
    ''' return list of configmaps referenced in a container spec '''
    configmap_refs = []
    if 'envFrom' in container_spec:
      for envfrom_spec in container_spec['envFrom']:
        if 'configMapRef' in envfrom_spec:
          configmap_refs += [
            envfrom_spec['configMapRef']['name']
          ]
    return sorted(configmap_refs)

  def extract_pod_spec(self, deployment_name):
    ''' extract pod spec from spec of specified deployment '''
    deployment_spec = self.get_resource_spec(
      'Deployment',
      deployment_name
    )
    if not deployment_spec['spec']['template']['spec']:
      raise HokusaiError(
        f'Pod spec in {deployment_name} deployment is empty.'
      )
    return deployment_spec['spec']['template']['spec']

  def get_resource_spec(self, kind, name=None):
    '''
    given 'kind' and 'metadata/name' of a Kubernetes resource,
    return its spec found in Hokusai yaml,
    if name is not specified,
    return the spec of the first resource matching kind
    '''
    right_kinds_spec = self.get_resources_by_kind(kind)
    for item in right_kinds_spec:
      if not name or item['metadata']['name'] == name:
        return item
    raise HokusaiError(
      f'Failed to find {name} {kind} resource in {self.template_file}'
    )

  def get_resources_by_kind(self, kind):
    ''' return specs of all resources found in Hokusai yaml matching kind '''
    spec = []
    yaml_spec = self.to_list()
    for item in yaml_spec:
      if item['kind'] == kind:
        spec += [item]
    return spec

  def to_file(self):
    ''' write rendered template to file '''
    path = write_temp_file(self.to_string(), HOKUSAI_TMP_DIR)
    self.tmp_filename = path
    return path

  def to_list(self):
    ''' convert rendered template to yaml list '''
    return list(yaml.safe_load_all(self.to_string()))

  def to_string(self):
    ''' render template file into string '''
    if self.render_template:
      template_config = {
        "project_name": config.project_name
      }

      try:
        template_config["project_repo"] = self.ecr.project_repo
      except NoCredentialsError:
        print_yellow(
          "WARNING: Could not get template variable project_repo"
        )

      if config.template_config_files:
        for template_config_file in config.template_config_files:
          try:
            config_loader = ConfigLoader(template_config_file)
            template_config.update(config_loader.load())
          except NoCredentialsError:
            print_yellow(
              f'WARNING: Could not get template config file {template_config_file}'
            )

      return TemplateRenderer(
        self.template_file, template_config
      ).render()
    else:
      with open(self.template_file, 'r') as f:
        content = f.read().strip()
      return content
