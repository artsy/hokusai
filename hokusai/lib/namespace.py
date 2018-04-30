from collections import OrderedDict
import yaml

from hokusai.lib.command import command
from hokusai.lib.exceptions import HokusaiError
from hokusai.lib.common import YAML_HEADER

@command
def create_new_app_yaml(source_file, app_name, destination_namespace):
  with open(source_file, 'r') as stream:
    try:
      yaml_content = list(yaml.load_all(stream))
    except yaml.YAMLError as exc:
      raise HokusaiError("Cannot read source yaml file %s." % source_file)

  for c in yaml_content: update_namespace(c, destination_namespace)

  new_namespace = OrderedDict([
      ('apiVersion', 'v1'),
      ('kind', 'Namespace'),
      ('metadata', {
        'name': destination_namespace
      })
    ])
  yaml_content = [new_namespace] + yaml_content

  with open("hokusai/%s.yml" % app_name, 'w') as output:
    output.write(YAML_HEADER)
    yaml.safe_dump_all(yaml_content, output, default_flow_style=False)

def update_namespace(yaml_section, destination_namespace):
  if 'apiVersion' in yaml_section:
    if 'metadata' in yaml_section:
      yaml_section['metadata']['namespace'] = destination_namespace
    else:
      yaml_section['metadata'] = { 'namespace': destination_namespace }
