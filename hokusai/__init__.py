import os
import sys
import signal

from subprocess import call, check_output
from collections import OrderedDict

import yaml

from hokusai.lib import representers

from jinja2 import Environment, PackageLoader
env = Environment(loader=PackageLoader('hokusai', 'templates'))

EXIT_SIGNALS = [signal.SIGHUP, signal.SIGINT, signal.SIGQUIT, signal.SIGPIPE, signal.SIGTERM]

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

def scaffold(language, base_image, app_name, port, target_port,
              with_memcached, with_redis, with_mongo, with_postgres):
  if language == 'ruby':
    dockerfile = env.get_template("Dockerfile-ruby.j2")
    command = 'bundle exec foreman start'
    test_command = 'bundle exec rspec'
    development_environment = ["RACK_ENV=development"]
    test_environment = ["RACK_ENV=test"]
  elif language == 'nodejs':
    dockerfile = env.get_template("Dockerfile-node.j2")
    command = 'node index.js'
    test_command = 'npm test'
    development_environment = ["NODE_ENV=development"]
    test_environment = ["NODE_ENV=test"]
  else:
    dockerfile = env.get_template("Dockerfile.j2")
    command = "service %s start" % app_name
    test_command = ''
    development_environment = []
    test_environment = []

  with open(os.path.join(os.getcwd(), 'Dockerfile'), 'w') as f:
    f.write(dockerfile.render(base_image=base_image, command=command, target_port=target_port))

  with open(os.path.join(os.getcwd(), 'development.yml'), 'w') as f:
    development_services = {
      app_name: {
        'build': '.',
        'ports': ["%s:%s" % (port, target_port)]
      }
    }

    development_services[app_name]['environment'] = development_environment

    if with_memcached:
      development_services['memcached'] = {
        'image': 'memcached',
        'ports': ["11211:11211"]
      }
      development_services[app_name]['environment'].append('MEMCACHED_SERVERS=memcached:11211')

    if with_redis:
      development_services['redis'] = {
        'image': 'redis:3.2-alpine',
        'ports': ["6379:6379"]
      }
      development_services[app_name]['environment'].append('REDIS_URL=redis://redis:6379/0')

    if with_mongo:
      development_services['mongodb'] = {
        'image': 'mongo:3.0',
        'ports': ["27017:27017"]
      }
      development_services[app_name]['environment'].append('MONGO_URL=mongodb://mongodb:27017/development')

    if with_postgres:
      development_services['postgres'] = {
        'image': 'postgres:9.4',
        'ports': ["5432:5432"]
      }
      development_services[app_name]['environment'].append('DATABASE_URL=postgresql://postgres/development')

    development_data = OrderedDict([
      ('version', '2'),
      ('services', development_services)
    ])
    f.write(yaml.safe_dump(development_data, default_flow_style=False))

  with open(os.path.join(os.getcwd(), 'test.yml'), 'w') as f:
    test_services = {
      'test': {
        'build': '.',
        'command': test_command
      }
    }

    test_services['test']['environment'] = test_environment

    if with_memcached:
      test_services['memcached'] = {
        'image': 'memcached',
        'ports': ["11211:11211"]
      }
      test_services['test']['environment'].append('MEMCACHED_SERVERS=memcached:11211')

    if with_redis:
      test_services['redis'] = {
        'image': 'redis:3.2-alpine',
        'ports': ["6379:6379"]
      }
      test_services['test']['environment'].append('REDIS_URL=redis://redis:6379/1')

    if with_mongo:
      test_services['mongodb'] = {
        'image': 'mongo:3.0',
        'ports': ["27017:27017"]
      }
      test_services['test']['environment'].append('MONGO_URL=mongodb://mongodb:27017/test')

    if with_postgres:
      test_services['postgres'] = {
        'image': 'postgres:9.4',
        'ports': ["5432:5432"]
      }
      test_services['test']['environment'].append('DATABASE_URL=postgresql://postgres/test')

    test_data = OrderedDict([
      ('version', '2'),
      ('services', test_services)
    ])
    f.write(yaml.safe_dump(test_data, default_flow_style=False))

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
  test_exit_code = int(check_output('docker wait ci_test_1', shell=True))

  # output the logs for the test (for clarity)
  call('docker logs ci_test_1', shell=True)

  # inspect the output of the test and display respective message
  if test_exit_code != 0:
    print('%sTests Failed%s - Exit Code: %s\n' % (RED, NC, test_exit_code))
  else:
    print("%sTests Passed%s" % (GREEN, NC))

  # cleanup
  call("docker-compose -f %s -p ci kill" % docker_compose_yml, shell=True)
  call("docker-compose -f %s -p ci rm -f" % docker_compose_yml, shell=True)

  sys.exit(test_exit_code)
