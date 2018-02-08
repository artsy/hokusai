import os

from hokusai.lib.command import command
from hokusai.lib.config import config
from hokusai.services.ecr import ECR
from hokusai.services.kubectl import Kubectl
from hokusai.lib.common import print_red, print_green, shout
from hokusai.lib.exceptions import CalledProcessError, HokusaiError

@command
def check():
  return_code = 0

  def check_ok(check_item):
    print_green(u'\u2714 ' + check_item + ' found')

  def check_err(check_item):
    print_red(u'\u2718 ' + check_item + ' not found')

  config.check()

  try:
    config.project_name
    check_ok('Config project-name')
  except HokusaiError:
    check_err('Config project-name')

  try:
    config.docker_repo
    check_ok('Config docker-repo')
  except HokusaiError:
    check_err('Config docker-repo')

  try:
    shout('docker --version')
    check_ok('docker')
  except CalledProcessError:
    check_err('docker')
    return_code += 1

  try:
    shout('docker-compose --version')
    check_ok('docker-compose')
  except CalledProcessError:
    check_err('docker-compose')
    return_code += 1

  try:
    shout('kubectl version')
    check_ok('kubectl')
  except CalledProcessError:
    check_err('kubectl')
    return_code += 1

  try:
    shout('git version')
    check_ok('git')
  except CalledProcessError:
    check_err('git')
    return_code += 1

  if os.environ.get('AWS_ACCESS_KEY_ID') is not None:
    check_ok('$AWS_ACCESS_KEY_ID')
  else:
    check_err('$AWS_ACCESS_KEY_ID')
    return_code += 1

  if os.environ.get('AWS_SECRET_ACCESS_KEY') is not None:
    check_ok('$AWS_SECRET_ACCESS_KEY')
  else:
    check_err('$AWS_SECRET_ACCESS_KEY')
    return_code += 1

  ecr = ECR()
  if ecr.project_repo_exists():
    check_ok("ECR repository '%s'" % config.project_name)
  else:
    check_err("ECR repository '%s'" % config.project_name)
    return_code += 1

  if os.path.isfile(os.path.join(os.getcwd(), 'hokusai/common.yml')):
    check_ok('./hokusai/common.yml')
  else:
    check_err('./hokusai/common.yml')
    return_code += 1

  if os.path.isfile(os.path.join(os.getcwd(), 'hokusai/development.yml')):
    check_ok('./hokusai/development.yml')
  else:
    check_err('./hokusai/development.yml')
    return_code += 1

  if os.path.isfile(os.path.join(os.getcwd(), 'hokusai/test.yml')):
    check_ok('./hokusai/test.yml')
  else:
    check_err('./hokusai/test.yml')
    return_code += 1

  for context in ['staging', 'production']:
    if context in Kubectl('staging').contexts():
      check_ok("kubectl context '%s'" % context)
    else:
      check_err("kubectl context '%s'" % context)
      return_code += 1

    if os.path.isfile(os.path.join(os.getcwd(), "hokusai/%s.yml" % context)):
      check_ok("./hokusai/%s.yml" % context)
    else:
      check_err("./hokusai/%s.yml" % context)
      return_code += 1

  return return_code
