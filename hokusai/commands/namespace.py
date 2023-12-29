import os

import json
import yaml

from collections import OrderedDict

from hokusai import CWD
from hokusai.lib.exceptions import HokusaiError
from hokusai.lib.common import print_green, clean_string, shout
from hokusai.lib.config import HOKUSAI_CONFIG_DIR, config
from hokusai.lib.constants import YAML_HEADER
from hokusai.services.kubectl import Kubectl
from hokusai.services.yaml_spec import YamlSpec


def create_new_app_yaml(source_file, app_name):
  yaml_spec = YamlSpec(source_file).to_file()
  with open(yaml_spec, 'r') as stream:
    try:
      yaml_content = list(yaml.load_all(stream, Loader=yaml.FullLoader))
    except yaml.YAMLError as exc:
      raise HokusaiError("Cannot read source yaml file %s." % source_file)

  for c in yaml_content: update_namespace(c, clean_string(app_name))

  new_namespace = OrderedDict([
      ('apiVersion', 'v1'),
      ('kind', 'Namespace'),
      ('metadata', {
        'name': clean_string(app_name),
        'labels': {
          'app-name': config.project_name,
          'app-phase': 'review'
        }
      })
    ])
  yaml_content = [new_namespace] + yaml_content

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
  if 'apiVersion' in yaml_section:
    if 'metadata' in yaml_section:
      yaml_section['metadata']['namespace'] = destination_namespace
    else:
      yaml_section['metadata'] = { 'namespace': destination_namespace }
