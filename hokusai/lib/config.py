import os
import sys

from collections import OrderedDict

import yaml

from hokusai.lib.common import print_red, YAML_HEADER
from hokusai.lib.exceptions import HokusaiError

HOKUSAI_ENV_VAR_PREFIX = 'HOKUSAI_'
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

  def get(self, key, default=None, use_env=False, _type=str):
    if use_env:
      value = self._env_value_for(key, _type)
      if value is not None:
        return value

    value = self._config_value_for(key, _type)
    if value is not None:
      return value

    return default

  def _env_value_for(self, key, _type):
    env_var = HOKUSAI_ENV_VAR_PREFIX + key.upper().replace('-', '_')
    val = os.environ.get(env_var)
    if val is None:
      return val
    try:
      return _type(val)
    except ValueError:
      raise HokusaiError("Environment variable %s could not be cast to %s" % (env_var, _type))

  def _config_value_for(self, key, _type):
    self.check()
    with open(HOKUSAI_CONFIG_FILE, 'r') as config_file:
      config_struct = yaml.safe_load(config_file.read())
      try:
        val = config_struct[key]
      except KeyError:
        return None
      if not isinstance(val, _type):
        raise HokusaiError("Config key %s is not of %s" % (key, _type))
      return val


  @property
  def project_name(self):
    project = self.get('project-name')
    if project is None:
      raise HokusaiError("Unconfigured 'project-name'! Plz check ./hokusai/config.yml")
    return project

  @property
  def pre_deploy(self):
    return self.get('pre-deploy')

  @property
  def post_deploy(self):
    return self.get('post-deploy')

  @property
  def git_remote(self):
    return self.get('git-remote')

  @property
  def run_tty(self):
    return self.get('run-tty', default=False, use_env=True, _type=bool)

config = HokusaiConfig()
