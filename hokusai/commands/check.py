import boto3
import os

import botocore.exceptions as botoexceptions

from hokusai import CWD
from hokusai.lib.command import command
from hokusai.lib.config import HOKUSAI_CONFIG_DIR, config
from hokusai.services.ecr import ECR
from hokusai.services.kubectl import Kubectl
from hokusai.lib.common import get_region_name, print_red, print_green, shout
from hokusai.lib.exceptions import CalledProcessError, HokusaiError

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
  except botoexceptions.ClientError, botoexceptions.NoCredentialsError:
    check_err('Valid AWS credentials')
    return_code += 1

  ecr = ECR()
  if ecr.project_repo_exists():
    check_ok("ECR repository '%s'" % config.project_name)
  else:
    check_err("ECR repository '%s'" % config.project_name)
    return_code += 1

  if not os.path.isfile(os.path.join(CWD, HOKUSAI_CONFIG_DIR, 'build.yml')):
    if os.path.isfile(os.path.join(CWD, HOKUSAI_CONFIG_DIR, 'common.yml')):
      check_ok('./hokusai/common.yml')
    else:
      check_err('./hokusai/build.yml')
  else:
    check_ok('./hokusai/build.yml')
    return_code += 1

  if os.path.isfile(os.path.join(CWD, HOKUSAI_CONFIG_DIR, 'development.yml')):
    check_ok('./hokusai/development.yml')
  else:
    check_err('./hokusai/development.yml')
    return_code += 1

  if os.path.isfile(os.path.join(CWD, HOKUSAI_CONFIG_DIR, 'test.yml')):
    check_ok('./hokusai/test.yml')
  else:
    check_err('./hokusai/test.yml')
    return_code += 1

  for context in ['staging', 'production']:
    try:
      if context in Kubectl('staging').contexts():
        check_ok("kubectl context '%s'" % context)
      else:
        check_err("kubectl context '%s'" % context)
        return_code += 1

      if os.path.isfile(os.path.join(CWD, "hokusai/%s.yml" % context)):
        check_ok("./hokusai/%s.yml" % context)
      else:
        check_err("./hokusai/%s.yml" % context)
        return_code += 1
    except CalledProcessError:
      check_err('%s context' % context)
      return_code += 1

  return return_code
