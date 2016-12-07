import os
import sys
import signal

from subprocess import call, check_call, check_output, CalledProcessError
from collections import OrderedDict

import yaml

from hokusai import representers
from hokusai.config import HokusaiConfig, HokusaiConfigError
from hokusai.common import *

from jinja2 import Environment, PackageLoader
env = Environment(loader=PackageLoader('hokusai', 'templates'))

def configure(aws_account_id, aws_ecr_region):
  HokusaiConfig().create(aws_account_id, aws_ecr_region)

def push(from_test_build, tags):
  config = HokusaiConfig().check()

  login_command = check_output("aws ecr get-login --region %s" % config.get('aws-ecr-region'), shell=True)
  check_call(login_command, shell=True)

  if from_test_build:
    build = "ci_%s:latest" % APP_NAME
  else:
    check_call("docker build -t %s ." % APP_NAME, shell=True)
    build = "%s:latest" % APP_NAME

  for tag in tags:
    check_call("docker tag %s %s:%s" % (build, config.get('aws-ecr-registry'), tag), shell=True)
    check_call("docker push %s:%s" % (config.get('aws-ecr-registry'), tag), shell=True)


def scaffold(framework, base_image, run_command, development_command, test_command, port, target_port,
              with_memcached, with_redis, with_mongo, with_postgres):
  config = HokusaiConfig().check()

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

  else:
    dockerfile = env.get_template("Dockerfile.j2")
    if run_command is None:
      run_command = "service %s start" % APP_NAME
    if development_command is None:
      development_command = ''
    if test_command is None:
      test_command = ''
    runtime_environment = {
      'development': [],
      'test': [],
      'production': []
    }

  with open(os.path.join(os.getcwd(), 'Dockerfile'), 'w') as f:
    f.write(dockerfile.render(base_image=base_image, command=run_command, target_port=target_port))

  for idx, compose_environment in enumerate(['development', 'test']):
    with open(os.path.join(os.getcwd(), "%s.yml" % compose_environment), 'w') as f:
      services = {
        APP_NAME: {
          'build': '.',
          'ports': ["%s:%s" % (port, target_port)]
        }
      }

      if compose_environment == 'development':
        services[APP_NAME]['command'] = development_command
      if compose_environment == 'test':
        services[APP_NAME]['command'] = test_command

      services[APP_NAME]['environment'] = runtime_environment[compose_environment]

      if with_memcached:
        services['memcached'] = {
          'image': 'memcached',
          'ports': ["11211:11211"]
        }
        services[APP_NAME]['environment'].append('MEMCACHED_SERVERS=memcached:11211')

      if with_redis:
        services['redis'] = {
          'image': 'redis:3.2-alpine',
          'ports': ["6379:6379"]
        }
        services[APP_NAME]['environment'].append("REDIS_URL=redis://redis:6379/%d" % idx)

      if with_mongo:
        services['mongodb'] = {
          'image': 'mongo:3.0',
          'ports': ["27017:27017"],
          'command': 'mongod --smallfiles'
        }
        services[APP_NAME]['environment'].append("MONGO_URL=mongodb://mongodb:27017/%s" % compose_environment)

      if with_postgres:
        services['postgres'] = {
          'image': 'postgres:9.4',
          'ports': ["5432:5432"]
        }
        services[APP_NAME]['environment'].append("DATABASE_URL=postgresql://postgres/%s" % compose_environment)

      data = OrderedDict([
        ('version', '2'),
        ('services', services)
      ])
      payload = YAML_HEADER + yaml.safe_dump(data, default_flow_style=False)
      f.write(payload)

  with open(os.path.join(os.getcwd(), "production.yml"), 'w') as f:
    deployment_data = OrderedDict([
      ('apiVersion', 'extensions/v1beta1'),
      ('kind', 'Deployment'),
      ('metadata', {'name': APP_NAME}),
      ('spec', {
        'replicas': 1,
        'template': {
          'metadata': {
            'labels': {
              'app': APP_NAME
              },
              'name': APP_NAME,
              'namespace': 'default'
            },
            'spec': {
              'containers': [
                {
                  'name': APP_NAME,
                  'image': "%s:latest" % config.get('aws-ecr-registry'),
                  'env': runtime_environment['production'],
                  'ports': [{'container_port': target_port}]
                }
              ]
            }
          }
        }
      )
    ])

    service_data = OrderedDict([
      ('apiVersion', 'extensions/v1beta1'),
      ('kind', 'Service'),
      ('metadata', {
        'labels': {'app': APP_NAME},
        'name': APP_NAME,
        'namespace': 'default'
      }),
      ('spec', {
        'ports': [{'port': port, 'targetPort': target_port, 'protocol': 'TCP'}],
        'selector': {'app': APP_NAME},
        'sessionAffinity': 'None',
        'type': 'LoadBalancer'
      })
    ])

    payload = YAML_HEADER + yaml.safe_dump(deployment_data, default_flow_style=False) + \
            YAML_HEADER + yaml.safe_dump(service_data, default_flow_style=False)
    f.write(payload)

def development(docker_compose_yml):
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
  # kill and remove any running containers
  def cleanup(*args):
    print('%sTests Failed For Unexpected Reasons%s\n' % (RED, NC))
    call("docker-compose -f %s -p ci kill" % docker_compose_yml, shell=True)
    call("docker-compose -f %s -p ci rm -f" % docker_compose_yml, shell=True)
    sys.exit(-1)

  # catch exit, do cleanup
  for sig in EXIT_SIGNALS:
    signal.signal(sig, cleanup)

  # build and run the composed services
  if call("docker-compose -f %s -p ci up --build -d" % docker_compose_yml, shell=True) != 0:
    print("%sDocker Compose Failed%s\n" % (RED, NC))
    sys.exit(-1)

  # wait for the test service to complete and grab the exit code
  test_exit_code = int(check_output("docker wait ci_%s_1" % APP_NAME, shell=True))

  # output the logs for the test (for clarity)
  call("docker logs ci_%s_1" % APP_NAME, shell=True)

  # inspect the output of the test and display respective message
  if test_exit_code != 0:
    print('%sTests Failed%s - Exit Code: %s\n' % (RED, NC, test_exit_code))
  else:
    print("%sTests Passed%s" % (GREEN, NC))

  # cleanup
  call("docker-compose -f %s -p ci kill" % docker_compose_yml, shell=True)
  call("docker-compose -f %s -p ci rm -f" % docker_compose_yml, shell=True)

  sys.exit(test_exit_code)
