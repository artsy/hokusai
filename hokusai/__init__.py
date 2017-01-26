import os
import sys
import signal
import urllib
import shutil
import base64
import getpass

from distutils.dir_util import mkpath
from subprocess import call, check_call, check_output, CalledProcessError, STDOUT
from collections import OrderedDict
from tempfile import NamedTemporaryFile

import yaml

from hokusai import representers
from hokusai.config import HokusaiConfig
from hokusai.common import *

from jinja2 import Environment, PackageLoader
env = Environment(loader=PackageLoader('hokusai', 'templates'))

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

def build():
  config = HokusaiConfig().check()
  docker_compose_yml = os.path.join(os.getcwd(), 'hokusai/common.yml')
  try:
    check_call("docker-compose -f %s build" % docker_compose_yml, shell=True)
    print_green("Built %s:latest" % config.project_name)
  except CalledProcessError:
    print_red('Build failed')
    return -1
  return 0

def push(test_build, tags):
  config = HokusaiConfig().check()

  try:
    login_command = check_output("aws ecr get-login --region %s" % config.aws_ecr_region, shell=True)
    check_call(login_command, shell=True)

    if test_build:
      build = "ci_%s:latest" % config.project_name
    else:
      build = "%s:latest" % config.project_name

    for tag in tags:
      check_call("docker tag %s %s:%s" % (build, config.aws_ecr_registry, tag), shell=True)
      check_call("docker push %s:%s" % (config.aws_ecr_registry, tag), shell=True)
      print_green("Pushed %s to %s:%s" % (build, config.aws_ecr_registry, tag))

  except CalledProcessError:
    print_red('Push failed')
    return -1

  return 0

def add_secret(context, key, value):
  config = HokusaiConfig().check()

  try:
    switch_context_result = check_output("kubectl config use-context %s" % context, stderr=STDOUT, shell=True)
    print_green("Switched context to %s" % context)
    if 'no context exists' in switch_context_result:
      print_red("Context %s does not exist.  Check ~/.kube/config" % context)
      return -1
    elif 'switched to context' in switch_context_result:
      try:
        existing_secrets = check_output("kubectl get secret %s-secrets -o yaml" % config.project_name, stderr=STDOUT, shell=True)
        secret_data = yaml.load(existing_secrets)['data']
      except CalledProcessError:
        secret_data = {}

      secret_data.update({key: base64.b64encode(value)})

      secret_yaml = OrderedDict([
        ('apiVersion', 'v1'),
        ('kind', 'Secret'),
        ('metadata', {
          'labels': {'app': config.project_name},
          'name': "%s-secrets" % config.project_name
        }),
        ('type', 'Opaque'),
        ('data', secret_data)
      ])

      f = NamedTemporaryFile(delete=False)
      f.write(yaml.safe_dump(secret_yaml, default_flow_style=False))
      f.close()
      check_output("kubectl apply -f %s" % f.name, stderr=STDOUT, shell=True)
      os.unlink(f.name)

  except CalledProcessError:
    print_red('Create secret failed')
    return -1

  print_green("Secret %s created" % key)
  return 0

def stack_up(context):
  config = HokusaiConfig().check()
  kubernetes_yml = os.path.join(os.getcwd(), "hokusai/%s.yml" % context)

  try:
    switch_context_result = check_output("kubectl config use-context %s" % context, stderr=STDOUT, shell=True)
    print_green("Switched context to %s" % context)
    if 'no context exists' in switch_context_result:
      print_red("Context %s does not exist.  Check ~/.kube/config" % context)
      return -1
    elif 'switched to context' in switch_context_result:
      check_call("kubectl apply -f %s" % kubernetes_yml, shell=True)
  except CalledProcessError:
    print_red('Stack up failed')
    return -1

  print_green("Stack %s created" % kubernetes_yml)
  return 0

def stack_down(context):
  config = HokusaiConfig().check()
  kubernetes_yml = os.path.join(os.getcwd(), "hokusai/%s.yml" % context)

  try:
    switch_context_result = check_output("kubectl config use-context %s" % context, stderr=STDOUT, shell=True)
    print_green("Switched context to %s" % context)
    if 'no context exists' in switch_context_result:
      print_red("Context %s does not exist.  Check ~/.kube/config" % context)
      return -1
    elif 'switched to context' in switch_context_result:
      check_call("kubectl delete -f %s" % kubernetes_yml, shell=True)
  except CalledProcessError:
    print_red('Stack down failed')
    return -1

  print_green("Stack %s deleted" % kubernetes_yml)
  return 0

def deploy(context, tag):
  config = HokusaiConfig().check()

  try:
    switch_context_result = check_output("kubectl config use-context %s" % context, stderr=STDOUT, shell=True)
    print_green("Switched context to %s" % context)
    if 'no context exists' in switch_context_result:
      print_red("Context %s does not exist.  Check ~/.kube/config" % context)
      return -1
    elif 'switched to context' in switch_context_result:
      check_call("kubectl set image deployment/%s %s=%s" % (config.project_name, config.project_name, "%s:%s" % (config.aws_ecr_registry, tag)), shell=True)
  except CalledProcessError:
    print_red('Deployment failed')
    return -1

  print_green("Deployment updated to %s" % tag)
  return 0

def init(project_name, aws_account_id, aws_ecr_region, framework, base_image,
          run_command, development_command, test_command, port, target_port,
            with_memcached, with_redis, with_mongo, with_postgres):

  mkpath(os.path.join(os.getcwd(), 'hokusai'))

  config = HokusaiConfig().create(project_name, aws_account_id, aws_ecr_region)

  if framework == 'rack':
    dockerfile = env.get_template("Dockerfile-ruby.j2")
    if run_command is None:
      run_command = 'bundle exec foreman start'
    if development_command is None:
      development_command = 'bundle exec foreman start'
    if test_command is None:
      test_command = 'bundle exec rspec'
    runtime_environment = {
      'development': ["RACK_ENV=development"],
      'test': ["RACK_ENV=test"],
      'staging': [{'name': 'RACK_ENV', 'value': 'staging'}],
      'production': [{'name': 'RACK_ENV', 'value': 'production'}]
    }

  elif framework == 'nodejs':
    dockerfile = env.get_template("Dockerfile-node.j2")
    if run_command is None:
      run_command = 'node index.js'
    if development_command is None:
      development_command = 'node index.js'
    if test_command is None:
      test_command = 'npm test'
    runtime_environment = {
      'development': ["NODE_ENV=development"],
      'test': ["NODE_ENV=test"],
      'staging': [{'name': 'NODE_ENV', 'value': 'staging'}],
      'production': [{'name': 'NODE_ENV', 'value': 'production'}]
    }

  with open(os.path.join(os.getcwd(), 'Dockerfile'), 'w') as f:
    f.write(dockerfile.render(base_image=base_image, command=run_command, target_port=target_port))

  with open(os.path.join(os.getcwd(), 'hokusai', "common.yml"), 'w') as f:
    services = {
      config.project_name: {
        'build': '../'
      }
    }
    data = OrderedDict([
        ('version', '2'),
        ('services', services)
      ])
    payload = YAML_HEADER + yaml.safe_dump(data, default_flow_style=False)
    f.write(payload)

  for idx, compose_environment in enumerate(['development', 'test']):
    with open(os.path.join(os.getcwd(), 'hokusai', "%s.yml" % compose_environment), 'w') as f:
      services = {
        config.project_name: {
          'extends': {
            'file': 'common.yml',
            'service': config.project_name
          }
        }
      }

      if compose_environment == 'development':
        services[config.project_name]['command'] = development_command
        services[config.project_name]['ports'] = ["%s:%s" % (port, target_port)]
      if compose_environment == 'test':
        services[config.project_name]['command'] = test_command

      services[config.project_name]['environment'] = runtime_environment[compose_environment]

      if with_memcached:
        services['memcached'] = {
          'image': 'memcached'
        }
        if compose_environment == 'development':
          services['memcached']['ports'] = ["11211:11211"]
        services[config.project_name]['environment'].append('MEMCACHED_SERVERS=memcached:11211')

      if with_redis:
        services['redis'] = {
          'image': 'redis:3.2-alpine'
        }
        if compose_environment == 'development':
          services['redis']['ports'] = ["6379:6379"]
        services[config.project_name]['environment'].append("REDIS_URL=redis://redis:6379/%d" % idx)

      if with_mongo:
        services['mongodb'] = {
          'image': 'mongo:3.0',
          'command': 'mongod --smallfiles'
        }
        if compose_environment == 'development':
          services['mongodb']['ports'] = ["27017:27017"]
        services[config.project_name]['environment'].append("MONGO_URL=mongodb://mongodb:27017/%s" % compose_environment)

      if with_postgres:
        services['postgres'] = {
          'image': 'postgres:9.4'
        }
        if compose_environment == 'development':
          services['postgres']['ports'] = ["5432:5432"]
        services[config.project_name]['environment'].append("DATABASE_URL=postgresql://postgres/%s" % compose_environment)

      data = OrderedDict([
        ('version', '2'),
        ('services', services)
      ])
      payload = YAML_HEADER + yaml.safe_dump(data, default_flow_style=False)
      f.write(payload)

  for stack in ['staging', 'production']:
    with open(os.path.join(os.getcwd(), 'hokusai', "%s.yml" % stack), 'w') as f:
      environment = runtime_environment[stack]

      if with_memcached:
        environment.append({'name': 'MEMCACHED_SERVERS', 'value': "%s-memcached:11211" % config.project_name})
      if with_redis:
        environment.append({'name': 'REDIS_URL', 'value': "redis://%s-redis:6379/0" % config.project_name})
      if with_mongo:
        environment.append({'name': 'MONGO_URL', 'value': "mongodb://%s-mongodb:27017/%s" % (config.project_name, stack)})
      if with_postgres:
        environment.append({'name': 'DATABASE_URL', 'value': "postgresql://%s-postgres/%s" % (config.project_name, stack)})

      deployment_data = build_deployment(config.project_name,
                                          "%s:latest" % config.aws_ecr_registry,
                                          target_port, environment=environment, always_pull=True)

      service_data = build_service(config.project_name, port, target_port=target_port, internal=False)

      stack_yaml = deployment_data + service_data

      if with_memcached:
        stack_yaml += build_deployment("%s-memcached" % config.project_name, 'memcached', 11211)
        stack_yaml += build_service("%s-memcached" % config.project_name, 11211)

      if with_redis:
        stack_yaml += build_deployment("%s-redis" % config.project_name, 'redis:3.2-alpine', 6379)
        stack_yaml += build_service("%s-redis" % config.project_name, 6379)

      if with_mongo:
        stack_yaml += build_deployment("%s-mongodb" % config.project_name, 'mongodb:3.0', 27017)
        stack_yaml += build_service("%s-mongodb" % config.project_name, 27017)

      if with_postgres:
        stack_yaml += build_deployment("%s-postgres" % config.project_name, 'postgres:9.4', 5432)
        stack_yaml += build_service("%s-postgres" % config.project_name, 5432)

      f.write(stack_yaml)

  print_green("Config created in ./hokusai")

def development():
  config = HokusaiConfig().check()
  docker_compose_yml = os.path.join(os.getcwd(), 'hokusai/development.yml')

  # exit cleanly
  def cleanup(*args):
    return 0

  # catch exit
  for sig in EXIT_SIGNALS:
    signal.signal(sig, cleanup)

  # build and run the composed services
  call("docker-compose -f %s up --build" % docker_compose_yml, shell=True)

def test():
  config = HokusaiConfig().check()
  docker_compose_yml = os.path.join(os.getcwd(), 'hokusai/test.yml')

  # stop any running containers
  def cleanup(*args):
    print_red('Tests Failed For Unexpected Reasons\n')
    call("docker-compose -f %s -p ci stop" % docker_compose_yml, shell=True)
    return -1

  # catch exit, do cleanup
  for sig in EXIT_SIGNALS:
    signal.signal(sig, cleanup)

  # build and run the composed services
  if call("docker-compose -f %s -p ci up --build -d" % docker_compose_yml, shell=True) != 0:
    print_red("Docker Compose Failed\n")
    return -1

  # wait for the test service to complete and grab the exit code
  try:
    test_exit_code = int(check_output("docker wait ci_%s_1" % config.project_name, shell=True))
  except CalledProcessError:
    print_red('Docker wait failed.')
    call("docker-compose -f %s -p ci stop" % docker_compose_yml, shell=True)
    return -1

  # output the logs for the test (for clarity)
  call("docker logs ci_%s_1" % config.project_name, shell=True)

  # inspect the output of the test and display respective message
  if test_exit_code != 0:
    print_red('Tests Failed - Exit Code: %s\n' % test_exit_code)
  else:
    print_green("Tests Passed")

  # cleanup
  call("docker-compose -f %s -p ci stop" % docker_compose_yml, shell=True)

  return test_exit_code
