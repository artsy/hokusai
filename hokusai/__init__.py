import os
import sys
import signal
import urllib
import shutil

from distutils.dir_util import mkpath
from subprocess import call, check_call, check_output, CalledProcessError, STDOUT
from collections import OrderedDict

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
        try:
          import pip
          pip.main(['install'], 'docker-compose')
        except Exception, e:
          print('pip install docker-compose failed with error %s' % e.message)

  try:
    check_output('aws --version', stderr=STDOUT, shell=True)
    check_ok('aws cli')
  except CalledProcessError:
    check_err('aws cli')
    return_code += 1

    if interactive:
      install_aws_cli = raw_input('Do you want to install the aws cli? --> ')
      if install_aws_cli in ['y', 'Y', 'yes', 'Yes', 'YES']:
        try:
          import pip
          pip.main(['install'], 'aws')
        except Exception, e:
          print('pip install aws failed with error %s' % e.message)

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

        mkpath('/tmp')

        print("Downloading and installing kubectl %s to %s ..." % (kubectl_version, install_to))
        urllib.urlretrieve("https://storage.googleapis.com/kubernetes-release/release/v%s/bin/%s/amd64/kubectl" % (kubectl_version, platform), os.path.join('/tmp', 'kubectl'))
        os.chmod(os.path.join('/tmp', 'kubectl'), 0755)
        shutil.move(os.path.join('/tmp', 'kubectl'), os.path.join(install_to, 'kubectl'))

        mkpath(os.path.join(os.environ.get('HOME'), '.kube'))
        print("Now install your organization's kubectl config to ~/.kube/config")

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

  if os.path.isfile(os.path.join(os.getcwd(), 'hokusai/production.yml')):
    check_ok('hokusai/production.yml')
  else:
    check_err('hokusai/production.yml')
    return_code += 1

  sys.exit(return_code)

def push(from_test_build, tags):
  config = HokusaiConfig().check()

  try:
    login_command = check_output("aws ecr get-login --region %s" % config.get('aws-ecr-region'), shell=True)
    check_call(login_command, shell=True)

    if from_test_build:
      build = "ci_%s:latest" % config.get('project-name')
    else:
      check_call("docker build -t %s ." % config.get('project-name'), shell=True)
      build = "%s:latest" % config.get('project-name')

    for tag in tags:
      check_call("docker tag %s %s:%s" % (build, config.get('aws-ecr-registry'), tag), shell=True)
      check_call("docker push %s:%s" % (config.get('aws-ecr-registry'), tag), shell=True)
  except CalledProcessError:
    print_red('Push failed')
    sys.exit(-1)

  print_green("Pushed %s" % build)

def stack_up(context, kubernetes_yml):
  config = HokusaiConfig().check()

  try:
    switch_context_result = check_output("kubectl config use-context %s" % context, stderr=STDOUT, shell=True)
    print_green("Switched context to %s" % context)
    if 'no context exists' in switch_context_result:
      print_red("Context %s does not exist.  Check ~/.kube/config" % context)
      sys.exit(-1)
    elif 'switched to context' in switch_context_result:
      check_call("kubectl create -f %s" % kubernetes_yml, shell=True)
  except CalledProcessError:
    print_red('Stack up failed')
    sys.exit(-1)

  print_green("Stack %s created" % kubernetes_yml)

def stack_down(context, kubernetes_yml):
  config = HokusaiConfig().check()

  try:
    switch_context_result = check_output("kubectl config use-context %s" % context, stderr=STDOUT, shell=True)
    print_green("Switched context to %s" % context)
    if 'no context exists' in switch_context_result:
      print_red("Context %s does not exist.  Check ~/.kube/config" % context)
      sys.exit(-1)
    elif 'switched to context' in switch_context_result:
      check_call("kubectl delete -f %s" % kubernetes_yml, shell=True)
  except CalledProcessError:
    print_red('Stack down failed')
    sys.exit(-1)

  print_green("Stack %s deleted" % kubernetes_yml)

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
      'production': [{'name': 'NODE_ENV', 'value': 'production'}]
    }

  with open(os.path.join(os.getcwd(), 'Dockerfile'), 'w') as f:
    f.write(dockerfile.render(base_image=base_image, command=run_command, target_port=target_port))

  for idx, compose_environment in enumerate(['development', 'test']):
    with open(os.path.join(os.getcwd(), 'hokusai', "%s.yml" % compose_environment), 'w') as f:
      services = {
        config.get('project-name'): {
          'build': '../'
        }
      }

      if compose_environment == 'development':
        services[config.get('project-name')]['command'] = development_command
        services[config.get('project-name')]['ports'] = ["%s:%s" % (port, target_port)]
      if compose_environment == 'test':
        services[config.get('project-name')]['command'] = test_command

      services[config.get('project-name')]['environment'] = runtime_environment[compose_environment]

      if with_memcached:
        services['memcached'] = {
          'image': 'memcached'
        }
        if compose_environment == 'development':
          services['memcached']['ports'] = ["11211:11211"]
        services[config.get('project-name')]['environment'].append('MEMCACHED_SERVERS=memcached:11211')

      if with_redis:
        services['redis'] = {
          'image': 'redis:3.2-alpine'
        }
        if compose_environment == 'development':
          services['redis']['ports'] = ["6379:6379"]
        services[config.get('project-name')]['environment'].append("REDIS_URL=redis://redis:6379/%d" % idx)

      if with_mongo:
        services['mongodb'] = {
          'image': 'mongo:3.0',
          'command': 'mongod --smallfiles'
        }
        if compose_environment == 'development':
          services['mongodb']['ports'] = ["27017:27017"]
        services[config.get('project-name')]['environment'].append("MONGO_URL=mongodb://mongodb:27017/%s" % compose_environment)

      if with_postgres:
        services['postgres'] = {
          'image': 'postgres:9.4'
        }
        if compose_environment == 'development':
          services['postgres']['ports'] = ["5432:5432"]
        services[config.get('project-name')]['environment'].append("DATABASE_URL=postgresql://postgres/%s" % compose_environment)

      data = OrderedDict([
        ('version', '2'),
        ('services', services)
      ])
      payload = YAML_HEADER + yaml.safe_dump(data, default_flow_style=False)
      f.write(payload)

  with open(os.path.join(os.getcwd(), 'hokusai', "production.yml"), 'w') as f:
    containers = [
      {
        'name': config.get('project-name'),
        'image': "%s:latest" % config.get('aws-ecr-registry'),
        'env': runtime_environment['production'],
        'ports': [{'containerPort': target_port}]
      }
    ]

    if with_memcached:
      containers.append({
        'name': "%s-memcached" % config.get('project-name'),
        'image': 'memcached',
        'ports': [{'containerPort': 11211}]
      })
      containers[0]['env'].append({'name': 'MEMCACHED_SERVERS', 'value': "%s-memcached:11211" % config.get('project-name')})

    if with_redis:
      containers.append({
        'name': "%s-redis" % config.get('project-name'),
        'image': 'redis:3.2-alpine',
        'ports': [{'containerPort': 6379}]
      })
      containers[0]['env'].append({'name': 'REDIS_URL', 'value': "redis://%s-redis:6379/0" % config.get('project-name')})

    if with_mongo:
      containers.append({
        'name': "%s-mongodb" % config.get('project-name'),
        'image': 'mongo:3.0',
        'ports': [{'containerPort': 27017}]
      })
      containers[0]['env'].append({'name': 'MONGO_URL', 'value': "mongodb://%s-mongodb:27017/production" % config.get('project-name')})

    if with_postgres:
      containers.append({
        'name': "%s-postgres" % config.get('project-name'),
        'image': 'postgres:9.4',
        'ports': [{'containerPort': 5432}]
      })
      containers[0]['env'].append({'name': 'DATABASE_URL', 'value': "postgresql://%s-postgres/production" % config.get('project-name')})

    deployment_data = OrderedDict([
      ('apiVersion', 'extensions/v1beta1'),
      ('kind', 'Deployment'),
      ('metadata', {'name': config.get('project-name')}),
      ('spec', {
        'replicas': 1,
        'template': {
          'metadata': {
            'labels': {
              'app': config.get('project-name')
              },
              'name': config.get('project-name'),
              'namespace': 'default'
            },
            'spec': {
              'containers': containers
            }
          }
        }
      )
    ])

    service_data = OrderedDict([
      ('apiVersion', 'extensions/v1beta1'),
      ('kind', 'Service'),
      ('metadata', {
        'labels': {'app': config.get('project-name')},
        'name': config.get('project-name'),
        'namespace': 'default'
      }),
      ('spec', {
        'ports': [{'port': port, 'targetPort': target_port, 'protocol': 'TCP'}],
        'selector': {'app': config.get('project-name')},
        'sessionAffinity': 'None',
        'type': 'LoadBalancer'
      })
    ])

    payload = YAML_HEADER + yaml.safe_dump(deployment_data, default_flow_style=False) + \
            YAML_HEADER + yaml.safe_dump(service_data, default_flow_style=False)
    f.write(payload)

  print_green("Config created in ./hokusai")

def development(docker_compose_yml):
  config = HokusaiConfig().check()

  # kill and remove any running containers
  def cleanup(*args):
    call("docker-compose -f %s kill" % docker_compose_yml, shell=True)
    call("docker-compose -f %s rm -f" % docker_compose_yml, shell=True)
    sys.exit(0)

  # catch exit, do cleanup
  for sig in EXIT_SIGNALS:
    signal.signal(sig, cleanup)

  # build and run the composed services
  call("docker-compose -f %s up --build" % docker_compose_yml, shell=True)

def test(docker_compose_yml):
  config = HokusaiConfig().check()

  # kill and remove any running containers
  def cleanup(*args):
    print_red('Tests Failed For Unexpected Reasons\n')
    call("docker-compose -f %s -p ci kill" % docker_compose_yml, shell=True)
    call("docker-compose -f %s -p ci rm -f" % docker_compose_yml, shell=True)
    sys.exit(-1)

  # catch exit, do cleanup
  for sig in EXIT_SIGNALS:
    signal.signal(sig, cleanup)

  # build and run the composed services
  if call("docker-compose -f %s -p ci up --build -d" % docker_compose_yml, shell=True) != 0:
    print_red("Docker Compose Failed\n")
    sys.exit(-1)

  # wait for the test service to complete and grab the exit code
  try:
    test_exit_code = int(check_output("docker wait ci_%s_1" % config.get('project-name'), shell=True))
  except CalledProcessError:
    print_red('Docker wait failed.')
    call("docker-compose -f %s -p ci kill" % docker_compose_yml, shell=True)
    call("docker-compose -f %s -p ci rm -f" % docker_compose_yml, shell=True)
    sys.exit(-1)

  # output the logs for the test (for clarity)
  call("docker logs ci_%s_1" % config.get('project-name'), shell=True)

  # inspect the output of the test and display respective message
  if test_exit_code != 0:
    print_red('Tests Failed - Exit Code: %s\n' % test_exit_code)
  else:
    print_green("Tests Passed")

  # cleanup
  call("docker-compose -f %s -p ci kill" % docker_compose_yml, shell=True)
  call("docker-compose -f %s -p ci rm -f" % docker_compose_yml, shell=True)

  sys.exit(test_exit_code)
