import os
import sys

import yaml

from hokusai.common import *

class HokusaiConfigError(Exception):
  pass

class HokusaiConfig(object):
  def create(self, project_name, aws_account_id, aws_ecr_region):
    config = {
      'project-name': project_name,
      'aws-account-id': aws_account_id,
      'aws-ecr-region': aws_ecr_region,
      'aws-ecr-registry': "%s.dkr.ecr.%s.amazonaws.com/%s" % (aws_account_id, aws_ecr_region, project_name)
    }

    with open(HOKUSAI_CONFIG_FILE, 'w') as f:
      payload = YAML_HEADER + yaml.safe_dump(config, default_flow_style=False)
      f.write(payload)

    return self

  def check(self):
    if not os.path.isfile(HOKUSAI_CONFIG_FILE):
      print_red("Hokusai is not configured for this project - run 'hokusai configure'")
      sys.exit(-1)
    return self

  def get(self, key):
    self.check()

    config_file = open(HOKUSAI_CONFIG_FILE, 'r')
    config_data = config_file.read()
    config_file.close()
    config = yaml.safe_load(config_data)

    try:
      return config[key]
    except KeyError:
      return None

  def set(self, key, value):
    self.check()

    config_file = open(HOKUSAI_CONFIG_FILE, 'r')
    config_data = config_file.read()
    config_file.close()
    config = yaml.safe_load(config_data)

    config[key] = value
    with open(HOKUSAI_CONFIG_FILE, 'w') as f:
      payload = YAML_HEADER + yaml.safe_dump(config, default_flow_style=False)
      f.write(payload)

    return key, value
