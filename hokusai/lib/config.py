import os
import sys

from collections import OrderedDict

import yaml

from hokusai.lib.common import print_red, YAML_HEADER
from hokusai.lib.exceptions import HokusaiError

HOKUSAI_CONFIG_FILE = os.path.join(os.getcwd(), 'hokusai', 'config.yml')

class HokusaiConfig(object):
  def create(self, project_name):
    config = OrderedDict([
      ('project-name', project_name)
    ])

    with open(HOKUSAI_CONFIG_FILE, 'w') as f:
      payload = YAML_HEADER + yaml.safe_dump(config, default_flow_style=False)
      f.write(payload)

    return self

  def check(self):
    if not os.path.isfile(HOKUSAI_CONFIG_FILE):
      raise HokusaiError("Hokusai is not set up for this project - run 'hokusai setup'")
    return self

  def get(self, key, default=None, fallback_to_env=True):
    self.check()
    config_file = open(HOKUSAI_CONFIG_FILE, 'r')
    config_data = config_file.read()
    config_file.close()
    config = yaml.safe_load(config_data)
    try:
      return config[key]
    except KeyError:
      pass
    try:
      return config[key.replace('_', '-')]
    except KeyError:
      pass

    if fallback_to_env:
      return os.environ.get('HOKUSAI_' + key.upper(), default)

    return default

  @property
  def project_name(self):
    project = self.get('project_name', fallback_to_env=False)
    if project is None:
      raise HokusaiError("Unconfigured 'project-name'! Plz check ./hokusai/config.yml")
    return project

  @property
  def pre_deploy(self):
    return self.get('pre_deploy', fallback_to_env=False)

  @property
  def post_deploy(self):
    return self.get('post_deploy', fallback_to_env=False)

  @property
  def git_remote(self):
    return self.get('git_remote')

config = HokusaiConfig()
