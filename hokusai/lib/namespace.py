from collections import OrderedDict
import yaml
from hokusai.lib.exceptions import HokusaiError

def create_new_app_yaml(source_file, app_name, destination_namespace):
  with open(source_file, 'r') as stream:
    try:
      yaml_content = list(yaml.load_all(stream))
      # update namespace to destination namespace
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
        yaml.safe_dump_all(yaml_content, output, default_flow_style=False)
    except yaml.YAMLError as exc:
      raise HokusaiError("Cannot read source yaml.")

def update_namespace(yaml_section, destination_namespace):
  if 'namespace' in yaml_section: yaml_section['namespace'] = destination_namespace
  for _k, v in yaml_section.iteritems():
    if isinstance(v, dict):
      update_namespace(v, destination_namespace)
