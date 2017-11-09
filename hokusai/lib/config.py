import os
import sys

from collections import OrderedDict

import yaml

from hokusai.lib.common import print_red, YAML_HEADER
from hokusai.lib.exceptions import HokusaiError

HOKUSAI_CONFIG_FILE = os.path.join(os.getcwd(), 'hokusai', 'config.yml')

class HokusaiConfig(object):
  def create(self, project_name, aws_account_id, aws_ecr_region):
    config = OrderedDict([
      ('aws-account-id', aws_account_id),
      ('aws-ecr-region', aws_ecr_region),
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

  @property
  def project_name(self):
    return self.get('project-name')

  @property
  def aws_account_id(self):
    return str(self.get('aws-account-id'))

  @property
  def aws_ecr_region(self):
    return self.get('aws-ecr-region')

  @property
  def aws_ecr_registry(self):
    return "%s.dkr.ecr.%s.amazonaws.com/%s" % (self.aws_account_id, self.aws_ecr_region, self.project_name)

  @property
  def pre_deploy(self):
    return self.get('pre-deploy')

  @property
  def post_deploy(self):
    return self.get('post-deploy')

config = HokusaiConfig()
