import os
import sys
import shutil
import atexit

from collections import OrderedDict

import yaml

from packaging.specifiers import SpecifierSet, InvalidSpecifier
from packaging.version import Version, InvalidVersion

from hokusai import CWD
from hokusai.lib.constants import YAML_HEADER
from hokusai.lib.exceptions import HokusaiError
from hokusai.version import VERSION

HOKUSAI_ENV_VAR_PREFIX = 'HOKUSAI_'
HOKUSAI_CONFIG_DIR = 'hokusai'
HOKUSAI_TMP_DIR = os.path.join(CWD, '.hokusai-tmp')
HOKUSAI_CONFIG_FILE = os.path.join(CWD, HOKUSAI_CONFIG_DIR, 'config.yml')
BUILD_YAML_FILE = 'build'
TEST_YML_FILE = 'test'
DEVELOPMENT_YML_FILE = 'development'

class HokusaiConfig(object):
  def __init__(self):
    if not os.path.isdir(HOKUSAI_TMP_DIR):
      os.mkdir(HOKUSAI_TMP_DIR)

  def create(self, project_name):
    config = OrderedDict([
      ('project-name', project_name)
    ])

    with open(HOKUSAI_CONFIG_FILE, 'w') as f:
      payload = YAML_HEADER + yaml.safe_dump(config, default_flow_style=False)
      f.write(payload)

  def check(self):
    if not self._check_config_present(HOKUSAI_CONFIG_FILE):
      raise HokusaiError("Hokusai is not set up for this project - run 'hokusai setup'")
    if not self._check_required_version(self.hokusai_required_version, VERSION):
      raise HokusaiError("Hokusai's current version %s does not satisfy this project's version requirements '%s'.  Aborting."
                           % (VERSION, self.hokusai_required_version))

  def _check_config_present(self, config_file):
    return os.path.isfile(config_file)

  def _check_required_version(self, required_version, target_version):
    if required_version is None:
      return True
    try:
      match_versions = SpecifierSet(required_version)
    except InvalidSpecifier:
      raise HokusaiError("Could not parse '%s' as a valid version specifier. See https://www.python.org/dev/peps/pep-0440/#version-specifiers" % required_version)
    try:
      compare_version = Version(target_version)
    except InvalidVersion:
      raise HokusaiError("Could not parse '%s' as a valid version identifier. See https://www.python.org/dev/peps/pep-0440/#version-scheme" % target_version)
    return compare_version in match_versions

  def get(self, key, default=None, use_env=False, _type=str):
    value = self._config_value_for(key, _type)
    if value is not None:
      return value

    if use_env:
      value = self._env_value_for(key, _type)
      if value is not None:
        return value

    return default

  def _env_value_for(self, key, _type):
    env_var = HOKUSAI_ENV_VAR_PREFIX + key.upper().replace('-', '_')
    val = os.environ.get(env_var)
    if val is None:
      return val
    if _type == list:
      try:
        return _type(val.split(','))
      except ValueError:
        raise HokusaiError("Environment variable %s could not be split to %s" % (env_var, _type))
    try:
      return _type(val)
    except ValueError:
      raise HokusaiError("Environment variable %s could not be cast to %s" % (env_var, _type))

  def _config_value_for(self, key, _type):
    try:
      with open(HOKUSAI_CONFIG_FILE, 'r') as config_file:
        config_struct = yaml.safe_load(config_file.read())
        try:
          val = config_struct[key]
        except KeyError:
          return None
        if not isinstance(val, _type):
          raise HokusaiError("Config key %s is not of %s" % (key, _type))
        return val
    except IOError:
      return None


  @property
  def project_name(self):
    project = self.get('project-name')
    if project is None:
      raise HokusaiError("Unconfigured 'project-name'! Plz check ./hokusai/config.yml")
    return project

  @property
  def hokusai_required_version(self):
    return self.get('hokusai-required-version')

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
  def pre_build(self):
    return self.get('pre-build')

  @property
  def post_build(self):
    return self.get('post-build')

  @property
  def template_config_files(self):
    return self.get('template-config-files', _type=list)

  @property
  def run_tty(self):
    return self.get('run-tty', default=False, use_env=True, _type=bool)

  @property
  def run_constraints(self):
    return self.get('run-constraints', default=[], use_env=True, _type=list)

  @property
  def follow_logs(self):
    return self.get('follow-logs', default=False, use_env=True, _type=bool)

  @property
  def tail_logs(self):
    return self.get('tail-logs', use_env=True, _type=int)

  @property
  def always_verbose(self):
    return self.get('always-verbose', default=False, use_env=True, _type=bool)

config = HokusaiConfig()
