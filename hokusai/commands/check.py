import os
import urllib
import shutil
import getpass
from distutils.dir_util import mkpath

from subprocess import check_output, CalledProcessError, STDOUT

from hokusai.common import print_red, print_green

def check(interactive):
  return_code = 0

  def check_ok(check_item):
    print_green(u'\u2714 ' + check_item + ' found')

  def check_err(check_item):
    print_red(u'\u2718 ' + check_item + ' not found')

  try:
    check_output('docker --version', stderr=STDOUT, shell=True)
    check_ok('docker')
  except CalledProcessError:
    check_err('docker')
    return_code += 1

  try:
    check_output('docker-compose --version', stderr=STDOUT, shell=True)
    check_ok('docker-compose')
  except CalledProcessError:
    check_err('docker-compose')
    return_code += 1

    if interactive:
      install_docker_compose = raw_input('Do you want to install docker-compose? --> ')
      if install_docker_compose in ['y', 'Y', 'yes', 'Yes', 'YES']:
        pwd = getpass.getpass('Enter your root password: ')
        try:
          check_output("echo %s | sudo -S pip install docker-compose" % pwd, stderr=STDOUT, shell=True)
          print_green('docker-compose installed')
        except CalledProcessError:
          print_red("'sudo pip install docker-compose' failed")

  try:
    check_output('aws --version', stderr=STDOUT, shell=True)
    check_ok('aws cli')
  except CalledProcessError:
    check_err('aws cli')
    return_code += 1

    if interactive:
      install_aws_cli = raw_input('Do you want to install the aws cli? --> ')
      if install_aws_cli in ['y', 'Y', 'yes', 'Yes', 'YES']:
        pwd = getpass.getpass('Enter your root password: ')
        try:
          check_output("echo %s | sudo -S pip install awscli" % pwd, stderr=STDOUT, shell=True)
          print_green('aws cli installed')
        except CalledProcessError:
          print_red("'sudo pip install awscli' failed")

  try:
    check_output('kubectl', stderr=STDOUT, shell=True)
    check_ok('kubectl')
  except CalledProcessError:
    check_err('kubectl')
    return_code += 1

    if interactive:
      install_kubectl = raw_input('Do you want to install kubectl? --> ')
      if install_kubectl in ['y', 'Y', 'yes', 'Yes', 'YES']:
        platform = raw_input('platform (default: darwin) --> ')
        if not platform:
          platform = 'darwin'
        kubectl_version = raw_input('kubectl version (default: 1.4.0) --> ')
        if not kubectl_version:
          kubectl_version = '1.4.0'
        install_to = raw_input('install kubectl to (default: /usr/local/bin) --> ')
        if not install_to:
          install_to = '/usr/local/bin'
        try:
          print("Downloading and installing kubectl %s to %s ..." % (kubectl_version, install_to))
          urllib.urlretrieve("https://storage.googleapis.com/kubernetes-release/release/v%s/bin/%s/amd64/kubectl" % (kubectl_version, platform), os.path.join('/tmp', 'kubectl'))
          os.chmod(os.path.join('/tmp', 'kubectl'), 0755)
          shutil.move(os.path.join('/tmp', 'kubectl'), os.path.join(install_to, 'kubectl'))
          mkpath(os.path.join(os.environ.get('HOME'), '.kube'))
          print_green("kubectl installed")
          print_green("Now install your organization's kubectl config to ~/.kube/config")
        except Exception, e:
          print_red("Installing kubectl failed with error %s" % e.message)

  if os.path.isfile(os.path.join(os.environ.get('HOME'), '.kube', 'config')):
    check_ok('~/.kube/config')
  else:
    check_err('~/.kube/config')
    return_code += 1

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
