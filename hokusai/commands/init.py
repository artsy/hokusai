import os

from distutils.dir_util import mkpath
from collections import OrderedDict

import yaml

from jinja2 import Environment, PackageLoader
env = Environment(loader=PackageLoader('hokusai', 'templates'))

from hokusai.config import HokusaiConfig
from hokusai.common import print_green, build_service, build_deployment, YAML_HEADER

def init(project_name, aws_account_id, aws_ecr_region, framework, base_image,
          run_command, development_command, test_command, port, target_port,
            with_memcached, with_redis, with_mongo, with_postgres):

  mkpath(os.path.join(os.getcwd(), 'hokusai'))

  config = HokusaiConfig().create(project_name.lower(), aws_account_id, aws_ecr_region)

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

  elif framework == 'elixir':
    dockerfile = env.get_template("Dockerfile-elixir.j2")
    if run_command is None:
      run_command = 'mix run --no-halt'
    if development_command is None:
      development_command = 'mix run'
    if test_command is None:
      test_command = 'mix test'
    runtime_environment = {
      'development': ["MIX_ENV=dev"],
      'test': ["MIX_ENV=test"],
      'staging': [{'name': 'MIX_ENV', 'value': 'prod'}],
      'production': [{'name': 'MIX_ENV', 'value': 'prod'}]
    }

  with open(os.path.join(os.getcwd(), 'hokusai', '.gitignore'), 'w') as f:
    f.write('*-secrets.yml\n')

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
                                          "%s:%s" % (config.aws_ecr_registry, stack),
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
