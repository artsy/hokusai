import os
import sys

from subprocess import call
from collections import OrderedDict

import yaml

from hokusai.lib import representers

from jinja2 import Environment, PackageLoader
env = Environment(loader=PackageLoader('hokusai', 'templates'))

def scaffold(target, flavor, app_name, command, test_command, port, target_port, with_redis, with_mongo):
  dockerfile = env.get_template("Dockerfile-%s-%s.j2" % (flavor, target))
  with open(os.path.join(os.getcwd(), 'Dockerfile'), 'w') as f:
    f.write(dockerfile.render(command=command, target_port=target_port))

  with open(os.path.join(os.getcwd(), 'development.yml'), 'w') as f:
    development_services = {
      app_name: {
        'build': '.',
        'ports': ["%s:%s" % (port, target_port)]
      }
    }

    if with_redis or with_mongo:
      development_services[app_name]['environment'] = []

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

    if with_redis or with_mongo:
      test_services['test']['environment'] = []

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

    test_data = OrderedDict([
      ('version', '2'),
      ('services', test_services)
    ])
    f.write(yaml.safe_dump(test_data, default_flow_style=False))

def call_and_exit(command):
  sys.exit(call(command, shell=True))

def development(docker_compose_yml):
  command = """
  # kill and remove any running containers
  cleanup () {
    docker-compose -f %s kill
    docker-compose -f %s rm -f
  }

  # catch exit, do cleanup
  trap 'cleanup' HUP INT QUIT PIPE TERM

  # build and run the composed services
  docker-compose -f %s up --build
  """ % (docker_compose_yml, docker_compose_yml, docker_compose_yml)

  call_and_exit(command)

def test(docker_compose_yml):
  command = """
  # define some colors to use for output
  RED='\033[0;31m'
  GREEN='\033[0;32m'
  NC='\033[0m'

  # kill and remove any running containers
  cleanup () {
    docker-compose -f %s -p ci kill
    docker-compose -f %s -p ci rm -f
  }

  # catch unexpected failures, do cleanup and output an error message
  trap 'cleanup ; printf "${RED}Tests Failed For Unexpected Reasons${NC}\n"'\
    HUP INT QUIT PIPE TERM

  # build and run the composed services
  docker-compose -f %s -p ci up --build -d
  if [ $? -ne 0 ] ; then
    printf "${RED}Docker Compose Failed${NC}\n"
    exit -1
  fi

  # wait for the test service to complete and grab the exit code
  TEST_EXIT_CODE=`docker wait ci_test_1`

  # output the logs for the test (for clarity)
  docker logs ci_test_1

  # inspect the output of the test and display respective message
  if [ -z ${TEST_EXIT_CODE+x} ] || [ "$TEST_EXIT_CODE" -ne 0 ] ; then
    printf "${RED}Tests Failed${NC} - Exit Code: $TEST_EXIT_CODE\n"
  else
    printf "${GREEN}Tests Passed${NC}\n"
  fi

  # call the cleanup fuction
  cleanup

  # exit the script with the same code as the test service code
  exit $TEST_EXIT_CODE
  """ % (docker_compose_yml, docker_compose_yml, docker_compose_yml)

  call_and_exit(command)
