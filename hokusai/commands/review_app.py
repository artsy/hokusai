import os

import yaml

from hokusai import CWD
from hokusai.commands.kubernetes import k8s_delete
from hokusai.lib.common import (
  print_green,
  clean_string,
  local_to_local,
  unlink_file_if_not_debug,
  write_temp_file
)
from hokusai.lib.config import HOKUSAI_CONFIG_DIR, HOKUSAI_TMP_DIR, config
from hokusai.lib.constants import YAML_HEADER
from hokusai.services.kubectl import Kubectl
from hokusai.services.namespace import Namespace
from hokusai.services.yaml_spec import YamlSpec


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
  payload_string = YAML_HEADER + payload_string
  tmp_path = write_temp_file(
    payload_string, HOKUSAI_TMP_DIR
  )
  local_to_local(
    tmp_path,
    os.path.join(CWD, HOKUSAI_CONFIG_DIR),
    f'{app_name}.yml',
    create_target_dir=False
  )
  unlink_file_if_not_debug(tmp_path)
  print_green(f'Created {HOKUSAI_CONFIG_DIR}/{app_name}.yml')

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
  # create namespace
  labels = {
    'app-name': config.project_name,
    'app-phase': 'review'
  }
  namespace = clean_string(app_name)
  ns = Namespace('staging', namespace, labels)
  ns.create()
  print_green(f'Created {namespace} Kubernetes namespace.')
  create_yaml(source_file, app_name)
