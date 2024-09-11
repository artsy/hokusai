import os

import yaml

from hokusai import CWD
from hokusai.commands.kubernetes import k8s_delete
from hokusai.lib.common import (
  print_green,
  clean_string,
  local_to_local,
  unlink_file_if_not_debug,
  write_temp_file,
  yaml_content_with_header
)
from hokusai.lib.config import HOKUSAI_CONFIG_DIR, HOKUSAI_TMP_DIR, config
from hokusai.services.configmap import ConfigMap
from hokusai.services.kubectl import Kubectl
from hokusai.services.namespace import Namespace
from hokusai.services.service_account import ServiceAccount
from hokusai.services.yaml_spec import YamlSpec


def copy_configmap(name, destination_namespace):
  ''' copy configmap from default namespace to destination namespace '''
  source_configmap = ConfigMap('staging', name=name)
  destination_configmap = ConfigMap(
    'staging',
    name=name,
    namespace=destination_namespace
  )
  source_configmap.load()
  destination_configmap.struct['data'] = source_configmap.struct['data']
  destination_configmap.save()

def copy_sa(name, destination_namespace):
  ''' copy service account from default namespace to destination namespace '''
  source_sa = ServiceAccount('staging', name=name)
  source_sa.load()
  spec = source_sa.spec
  spec['metadata']['namespace'] = destination_namespace
  dest_sa = ServiceAccount(
    'staging',
    namespace=destination_namespace,
    name=name,
    spec=spec
  )
  dest_sa.apply()

def create_yaml(source_file, app_name):
  ''' create yaml for review app '''
  yaml_content = YamlSpec(source_file).to_list()
  namespace = clean_string(app_name)
  for k8s_resource in yaml_content:
    edit_namespace(k8s_resource, namespace)
  payload_string = yaml.safe_dump_all(
    yaml_content,
    default_flow_style=False
  )
  tmp_path = write_temp_file(
    yaml_content_with_header(payload_string),
    HOKUSAI_TMP_DIR
  )
  local_to_local(
    tmp_path,
    os.path.join(CWD, HOKUSAI_CONFIG_DIR),
    f'{app_name}.yml',
    create_target_dir=False
  )
  unlink_file_if_not_debug(tmp_path)
  path = f'{HOKUSAI_CONFIG_DIR}/{app_name}.yml'
  print_green(f'Created {path}')
  return path

def delete_review_app(context, app_name, filename):
  ''' delete review app '''
  namespace = clean_string(app_name)
  # delete resources in yaml
  k8s_delete(context, namespace, filename)
  # delete namespace
  ns = Namespace('staging', namespace)
  ns.delete()
  print_green(f'Deleted {namespace} Kubernetes namespace.')

def edit_namespace(k8s_resource, destination_namespace):
  ''' edit namespace field for a Kubernetes resource definition '''
  if 'apiVersion' in k8s_resource:
    struct = {
      'namespace': destination_namespace
    }
    k8s_resource['metadata'] = k8s_resource.setdefault(
      'metadata', struct
    ) | struct

def list_review_apps(context, labels=None):
  ''' list project's review apps '''
  kctl = Kubectl(context)
  namespaces = kctl.get_objects('namespaces', labels)
  for ns in namespaces:
    print(ns['metadata']['name'])

def setup_review_app(source_file, app_name):
  ''' prepare for creating a review app '''
  namespace = clean_string(app_name)

  # create namespace
  labels = {
    'app-name': config.project_name,
    'app-phase': 'review'
  }
  ns = Namespace('staging', namespace, labels)
  ns.create()
  print_green(f'Created {namespace} Kubernetes namespace.')

  # create yaml file
  path = create_yaml(source_file, app_name)

  # get list of configmaps referenced in yaml's Deployments
  # and copy them to review app namespace
  configmap_refs = YamlSpec(
    path,
    render_template=False
  ).all_deployments_configmap_refs()
  for configmap in configmap_refs:
    print_green(
      f'Copying {configmap} ConfigMap to {namespace} namespace...'
    )
    copy_configmap(configmap, namespace)

  # get list of service accounts referenced in yaml's Deployments
  # and copy them to review app namespace
  service_account_refs = YamlSpec(
    path,
    render_template=False
  ).all_deployments_sa_refs()
  for sa in service_account_refs:
    print_green(
      f'Copying {sa} ServiceAccount to {namespace} namespace...'
    )
    copy_sa(sa, namespace)
