import os

import json
import yaml

from collections import OrderedDict

from hokusai import CWD
from hokusai.commands.kubernetes import k8s_delete
from hokusai.lib.exceptions import HokusaiError
from hokusai.lib.common import print_green, clean_string, shout
from hokusai.lib.config import HOKUSAI_CONFIG_DIR, config
from hokusai.lib.constants import YAML_HEADER
from hokusai.services.kubectl import Kubectl
from hokusai.services.namespace import Namespace
from hokusai.services.yaml_spec import YamlSpec


def delete_review_app(context, app_name, filename):
  ''' delete review app '''
  namespace = clean_string(app_name)
  k8s_delete(context, namespace, filename)
  ns = Namespace('staging', namespace)
  ns.delete()
  print_green(f'Deleted {namespace} Kubernetes namespace.')

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

  # create review app yaml
  create_yaml(source_file, app_name)

def create_yaml(source_file, app_name):
  ''' create yaml for review app '''
  yaml_spec = YamlSpec(source_file).to_file()
  with open(yaml_spec, 'r') as stream:
    try:
      yaml_content = list(yaml.load_all(stream, Loader=yaml.FullLoader))
    except yaml.YAMLError as exc:
      raise HokusaiError("Cannot read source yaml file %s." % source_file)

  namespace = clean_string(app_name)
  for c in yaml_content: update_namespace(c, namespace)

  with open(os.path.join(CWD, HOKUSAI_CONFIG_DIR, "%s.yml" % app_name), 'w') as output:
    output.write(YAML_HEADER)
    yaml.safe_dump_all(yaml_content, output, default_flow_style=False)

  print_green("Created %s/%s.yml" % (HOKUSAI_CONFIG_DIR, app_name))

def list_namespaces(context, labels=None):
  ''' list Kubernetes namespaces that match the given labels '''
  kctl = Kubectl(context)
  namespaces = kctl.get_objects('namespaces', labels)
  for ns in namespaces:
    print(ns['metadata']['name'])

def update_namespace(yaml_section, destination_namespace):
  ''' edit namespace field for a Kubernetes resource definition '''
  if 'apiVersion' in yaml_section:
    if 'metadata' in yaml_section:
      yaml_section['metadata']['namespace'] = destination_namespace
    else:
      yaml_section['metadata'] = { 'namespace': destination_namespace }
