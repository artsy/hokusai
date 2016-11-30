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

def scaffold(framework, base_image, run_command, development_command, test_command, port, target_port,
              with_memcached, with_redis, with_mongo, with_postgres):
  app_name = os.path.basename(os.getcwd())

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
      'test': ["RACK_ENV=test"]
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
      'test': ["NODE_ENV=test"]
    }

  else:
    dockerfile = env.get_template("Dockerfile.j2")
    if run_command is None:
      run_command = "service %s start" % app_name
    if development_command is None:
      development_command = ''
    if test_command is None:
      test_command = ''
    runtime_environment = {
      'development': [],
      'test': []
    }

  with open(os.path.join(os.getcwd(), 'Dockerfile'), 'w') as f:
    f.write(dockerfile.render(base_image=base_image, command=run_command, target_port=target_port))

  for idx, compose_environment in enumerate(['development', 'test']):
    with open(os.path.join(os.getcwd(), "%s.yml" % compose_environment), 'w') as f:
      services = {
        app_name: {
          'build': '.',
          'ports': ["%s:%s" % (port, target_port)]
        }
      }

      if compose_environment == 'development':
        services[app_name]['command'] = development_command
      if compose_environment == 'test':
        services[app_name]['command'] = test_command

      services[app_name]['environment'] = runtime_environment[compose_environment]

      if with_memcached:
        services['memcached'] = {
          'image': 'memcached',
          'ports': ["11211:11211"]
        }
        services[app_name]['environment'].append('MEMCACHED_SERVERS=memcached:11211')

      if with_redis:
        services['redis'] = {
          'image': 'redis:3.2-alpine',
          'ports': ["6379:6379"]
        }
        services[app_name]['environment'].append("REDIS_URL=redis://redis:6379/%d" % idx)

      if with_mongo:
        services['mongodb'] = {
          'image': 'mongo:3.0',
          'ports': ["27017:27017"],
          'command': 'mongod --smallfiles'
        }
        services[app_name]['environment'].append("MONGO_URL=mongodb://mongodb:27017/%s" % compose_environment)

      if with_postgres:
        services['postgres'] = {
          'image': 'postgres:9.4',
          'ports': ["5432:5432"]
        }
        services[app_name]['environment'].append("DATABASE_URL=postgresql://postgres/%s" % compose_environment)

      data = OrderedDict([
        ('version', '2'),
        ('services', services)
      ])
      f.write(yaml.safe_dump(data, default_flow_style=False))


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
  app_name = os.path.basename(os.getcwd())
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
  test_exit_code = int(check_output("docker wait ci_%s_1" % app_name, shell=True))

  # output the logs for the test (for clarity)
  call("docker logs ci_%s_1" % app_name, shell=True)

  # inspect the output of the test and display respective message
  if test_exit_code != 0:
    print('%sTests Failed%s - Exit Code: %s\n' % (RED, NC, test_exit_code))
  else:
    print("%sTests Passed%s" % (GREEN, NC))

  # cleanup
  call("docker-compose -f %s -p ci kill" % docker_compose_yml, shell=True)
  call("docker-compose -f %s -p ci rm -f" % docker_compose_yml, shell=True)

  sys.exit(test_exit_code)
