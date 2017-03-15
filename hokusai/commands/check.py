import os

from hokusai.command import command
from hokusai.common import print_red, print_green, shout, CalledProcessError

@command
def check():
  return_code = 0

  def check_ok(check_item):
    print_green(u'\u2714 ' + check_item + ' found')

  def check_err(check_item):
    print_red(u'\u2718 ' + check_item + ' not found')

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
    shout('kubectl')
    check_ok('kubectl')
  except CalledProcessError:
    check_err('kubectl')
    return_code += 1

  if os.path.isfile(os.path.join(os.environ.get('HOME'), '.kube', 'config')):
    check_ok('~/.kube/config')
  else:
    check_err('~/.kube/config')
    return_code += 1

  if os.environ.get('AWS_ACCESS_KEY_ID') is not None:
    check_ok('AWS_ACCESS_KEY_ID')
  else:
    check_err('AWS_ACCESS_KEY_ID')

  if os.environ.get('AWS_SECRET_ACCESS_KEY') is not None:
    check_ok('AWS_SECRET_ACCESS_KEY')
  else:
    check_err('AWS_SECRET_ACCESS_KEY')

  if os.environ.get('AWS_REGION') is not None:
    check_ok('AWS_REGION')
  else:
    check_err('AWS_REGION')

  if os.environ.get('AWS_ACCOUNT_ID') is not None:
    check_ok('AWS_ACCOUNT_ID')
  else:
    check_err('AWS_ACCOUNT_ID')

  if os.path.isfile(os.path.join(os.getcwd(), 'hokusai/config.yml')):
    check_ok('hokusai/config.yml')
  else:
    check_err('hokusai/config.yml')
    return_code += 1

  if os.path.isfile(os.path.join(os.getcwd(), 'hokusai/common.yml')):
    check_ok('hokusai/common.yml')
  else:
    check_err('hokusai/common.yml')
    return_code += 1

  if os.path.isfile(os.path.join(os.getcwd(), 'hokusai/development.yml')):
    check_ok('hokusai/development.yml')
  else:
    check_err('hokusai/development.yml')
    return_code += 1

  if os.path.isfile(os.path.join(os.getcwd(), 'hokusai/test.yml')):
    check_ok('hokusai/test.yml')
  else:
    check_err('hokusai/test.yml')
    return_code += 1

  if os.path.isfile(os.path.join(os.getcwd(), 'hokusai/staging.yml')):
    check_ok('hokusai/staging.yml')
  else:
    check_err('hokusai/staging.yml')
    return_code += 1

  if os.path.isfile(os.path.join(os.getcwd(), 'hokusai/production.yml')):
    check_ok('hokusai/production.yml')
  else:
    check_err('hokusai/production.yml')
    return_code += 1

  return return_code
