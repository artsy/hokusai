import os

import yaml

from hokusai import CWD
from hokusai.lib.common import get_verbosity, print_green, print_yellow, shout
from hokusai.lib.config import HOKUSAI_CONFIG_DIR
from hokusai.lib.exceptions import CalledProcessError
from hokusai.lib.template_selector import TemplateSelector
from hokusai.services.yaml_spec import YamlSpec


def detect_compose_command():
  ''' decide what command to use for Docker Compose '''
  command_to_use = ''
  try:
    shout('which docker-compose')
    if get_verbosity():
      print_green('Found docker-compose.')
    command_to_use = 'docker-compose'
  except CalledProcessError:
    if get_verbosity():
      print_yellow(
        'docker-compose command not found. ' +
        'Will use "docker compose" assuming it exists.'
      )
    command_to_use = 'docker compose'
  return command_to_use

def follow_extends(docker_compose_yml):
  with open(docker_compose_yml, 'r') as f:
    rendered_templates = []
    struct = yaml.safe_load(f.read())
    for service_name, service_spec in list(struct['services'].items()):
      if 'extends' not in service_spec or 'file' not in service_spec['extends']:
        continue
      extended_filename = service_spec['extends']['file']
      extended_template_path = os.path.join(CWD, HOKUSAI_CONFIG_DIR, extended_filename)
      if not os.path.isfile(extended_template_path):
        extended_template_path = os.path.join(CWD, HOKUSAI_CONFIG_DIR, extended_filename + '.j2')
      extended_template = TemplateSelector().get(extended_template_path)
      rendered_templates.append(YamlSpec(extended_template).to_file())
    return rendered_templates

def generate_compose_command(filename, default_yaml_file):
  ''' return Docker Compose command '''
  docker_compose_yml = render_docker_compose_yml(
    filename,
    default_yaml_file
  )
  # docker-compose v2 switched to using '-' as separator in image name,
  # resulting in 'hokusai-<project>'
  # COMPOSE_COMPATIBILITY=true forces v2 to use '_',
  # resulting in 'hokusai_<project>', matching v1
  return (
    'COMPOSE_COMPATIBILITY=true ' +
    detect_compose_command() +
    f' -f {docker_compose_yml}'
  )

def get_yaml_template(filename, default_yaml_file):
  ''' return yaml template '''
  if filename is None:
    yaml_template = TemplateSelector().get(
      os.path.join(
        CWD,
        HOKUSAI_CONFIG_DIR,
        default_yaml_file
      )
    )
  else:
    yaml_template = TemplateSelector().get(filename)
  return yaml_template

def render_docker_compose_yml(filename, default_yaml_file):
  ''' return path of rendered Docker Compose yaml '''
  yaml_template = get_yaml_template(filename, default_yaml_file)
  docker_compose_yml = YamlSpec(yaml_template).to_file()
  follow_extends(docker_compose_yml)
  return docker_compose_yml
