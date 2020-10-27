import boto3
import os

import botocore.exceptions as botoexceptions

from hokusai import CWD
from hokusai.lib.command import command
from hokusai.lib.config import HOKUSAI_CONFIG_DIR, BUILD_YAML_FILE, TEST_YML_FILE, DEVELOPMENT_YML_FILE, config
from hokusai.services.ecr import ECR
from hokusai.services.kubectl import Kubectl
from hokusai.lib.common import get_region_name, print_red, print_green, shout
from hokusai.lib.exceptions import CalledProcessError, HokusaiError
from hokusai.lib.template_selector import TemplateSelector

@command()
def check():
  return_code = 0

  def check_ok(check_item):
    print_green(u'\u2714 ' + check_item + ' found')

  def check_err(check_item):
    print_red(u'\u2718 ' + check_item + ' not found')

  try:
    config.project_name
    check_ok('Config project-name')
  except HokusaiError:
    check_err('Config project-name')

  try:
    shout('which docker')
    check_ok('docker')
  except CalledProcessError:
    check_err('docker')
    return_code += 1

  try:
    shout('which docker-compose')
    check_ok('docker-compose')
  except CalledProcessError:
    check_err('docker-compose')
    return_code += 1

  try:
    shout('which kubectl')
    check_ok('kubectl')
  except CalledProcessError:
    check_err('kubectl')
    return_code += 1

  try:
    shout('which git')
    check_ok('git')
  except CalledProcessError:
    check_err('git')
    return_code += 1

  try:
    boto3.client('sts', region_name=get_region_name()).get_caller_identity()
    check_ok('Valid AWS credentials')
  except (botoexceptions.ClientError, botoexceptions.NoCredentialsError):
    check_err('Valid AWS credentials')
    return_code += 1

  ecr = ECR()
  if ecr.project_repo_exists():
    check_ok("ECR repository '%s'" % config.project_name)
  else:
    check_err("ECR repository '%s'" % config.project_name)
    return_code += 1

  try:
    build_template = TemplateSelector().get(os.path.join(CWD, HOKUSAI_CONFIG_DIR, BUILD_YAML_FILE))
    check_ok(HOKUSAI_CONFIG_DIR + '/' + os.path.split(build_template)[-1])
  except HokusaiError:
    check_err('hokusai/build.*')
    return_code += 1

  try:
    development_template = TemplateSelector().get(os.path.join(CWD, HOKUSAI_CONFIG_DIR, DEVELOPMENT_YML_FILE))
    check_ok(HOKUSAI_CONFIG_DIR + '/' + os.path.split(development_template)[-1])
  except HokusaiError:
    check_err('hokusai/development.*')
    return_code += 1

  try:
    test_template = TemplateSelector().get(os.path.join(CWD, HOKUSAI_CONFIG_DIR, TEST_YML_FILE))
    check_ok(HOKUSAI_CONFIG_DIR + '/' + os.path.split(test_template)[-1])
  except HokusaiError:
    check_err('hokusai/test.*')
    return_code += 1

  for context in ['staging', 'production']:
    try:
      if context in Kubectl('staging').contexts():
        check_ok("kubectl context '%s'" % context)
      else:
        check_err("kubectl context '%s'" % context)
        return_code += 1
    except CalledProcessError:
      check_err('%s context' % context)
      return_code += 1

    try:
      context_template = TemplateSelector().get(os.path.join(CWD, HOKUSAI_CONFIG_DIR, context))
      check_ok(HOKUSAI_CONFIG_DIR + '/' + os.path.split(context_template)[-1])
    except HokusaiError:
      check_err("hokusai/%s.*" % context)
      return_code += 1

  return return_code
