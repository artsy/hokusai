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

  def get(self, key, default=None, fallback_to_env=True, _type=str):
    value = self.__value_for(key)
    if value is not None:
      if not isinstance(value, _type):
        raise HokusaiError("Config key %s is not of %s" % (key, _type))
      return value

    if fallback_to_env is False:
      return default

    env_var_for_key = 'HOKUSAI_' + key.upper()
    value_from_env = os.environ.get(env_var_for_key)
    if value_from_env is None:
      return default

    try:
      return _type(value_from_env)
    except ValueError:
      raise HokusaiError("Environment variable %s could not be cast to %s" % (env_var_for_key, _type))


  def __value_for(self, key):
    self.check()
    with open(HOKUSAI_CONFIG_FILE, 'r') as config_file:
      config_struct = yaml.safe_load(config_file.read())
      try:
        return config_struct[key]
      except KeyError:
        pass
      try:
        return config_struct[key.replace('_', '-')]
      except KeyError:
        pass


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

  @property
  def run_tty(self):
    return self.get('run_tty', default=False, _type=bool)

config = HokusaiConfig()
