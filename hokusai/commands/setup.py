import os
import urllib

from distutils.dir_util import mkpath
from collections import OrderedDict

import yaml

from jinja2 import Environment, PackageLoader
env = Environment(loader=PackageLoader('hokusai', 'templates'))

from hokusai.lib.command import command
from hokusai.lib.config import config
from hokusai.services.ecr import ECR
from hokusai.lib.common import print_green, print_red, build_service, build_deployment, YAML_HEADER

@command
def setup(aws_account_id, project_type, project_name, aws_ecr_region, port,
          with_memcached, with_redis, with_mongodb, with_postgres, with_rabbitmq):

  mkpath(os.path.join(os.getcwd(), 'hokusai'))

  config.create(project_name.lower().replace('_', '-'), aws_account_id, aws_ecr_region)

  if project_type == 'ruby-rack':
    dockerfile = env.get_template("Dockerfile-ruby.j2")
    base_image = 'ruby:latest'
    run_command = 'bundle exec rackup'
    development_command = 'bundle exec rackup'
    test_command = 'bundle exec rake'
    runtime_environment = {
      'development': ["RACK_ENV=development"],
      'test': ["RACK_ENV=test"],
      'staging': [{'name': 'RACK_ENV', 'value': 'staging'}],
      'production': [{'name': 'RACK_ENV', 'value': 'production'}]
    }

  elif project_type == 'ruby-rails':
    dockerfile = env.get_template("Dockerfile-ruby.j2")
    base_image = 'ruby:latest'
    run_command = 'bundle exec rails server'
    development_command = 'bundle exec rails server'
    test_command = 'bundle exec rake'
    runtime_environment = {
      'development': ["RAILS_ENV=development"],
      'test': ["RAILS_ENV=test"],
      'staging': [{'name': 'RAILS_ENV', 'value': 'staging'}],
      'production': [{'name': 'RAILS_ENV', 'value': 'production'}]
    }

  elif project_type == 'nodejs':
    dockerfile = env.get_template("Dockerfile-node.j2")
    base_image = 'node:latest'
    run_command = 'node index.js'
    development_command = 'node index.js'
    test_command = 'npm test'
    runtime_environment = {
      'development': ["NODE_ENV=development"],
      'test': ["NODE_ENV=test"],
      'staging': [{'name': 'NODE_ENV', 'value': 'staging'}],
      'production': [{'name': 'NODE_ENV', 'value': 'production'}]
    }

  elif project_type == 'elixir':
    dockerfile = env.get_template("Dockerfile-elixir.j2")
    base_image = 'elixir:latest'
    run_command = 'mix run --no-halt'
    development_command = 'mix run'
    test_command = 'mix test'
    runtime_environment = {
      'development': ["MIX_ENV=dev"],
      'test': ["MIX_ENV=test"],
      'staging': [{'name': 'MIX_ENV', 'value': 'prod'}],
      'production': [{'name': 'MIX_ENV', 'value': 'prod'}]
    }

  elif project_type == 'python-wsgi':
    dockerfile = env.get_template("Dockerfile-python.j2")
    base_image = 'python:latest'
    run_command = "gunicorn -b 0.0.0.0:%s app" % port
    development_command = "python -m werkzeug.serving -b 0.0.0.0:%s %s" % (port, project_name)
    test_command = 'python -m unittest discover .'
    runtime_environment = {
      'development': ["PYTHON_ENV=development"],
      'test': ["PYTHON_ENV=test"],
      'staging': [{'name': 'PYTHON_ENV', 'value': 'staging'}],
      'production': [{'name': 'PYTHON_ENV', 'value': 'production'}]
    }

  with open(os.path.join(os.getcwd(), 'Dockerfile'), 'w') as f:
    f.write(dockerfile.render(base_image=base_image, command=run_command, target_port=port))

  with open(os.path.join(os.getcwd(), 'hokusai', "common.yml"), 'w') as f:
    services = {
      config.project_name: {
        'build': {
          'context': '../'
        }
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
        services[config.project_name]['ports'] = ["%s:%s" % (port, port)]
        services[config.project_name]['volumes'] = ['../:/app']
      if compose_environment == 'test':
        services[config.project_name]['command'] = test_command

      services[config.project_name]['environment'] = runtime_environment[compose_environment]

      if with_memcached or with_redis or with_mongodb or with_postgres or with_rabbitmq:
        services[config.project_name]['depends_on'] = []

      if with_memcached:
        services["%s-memcached" % config.project_name] = {
          'image': 'memcached'
        }
        if compose_environment == 'development':
          services["%s-memcached" % config.project_name]['ports'] = ["11211:11211"]
        services[config.project_name]['environment'].append("MEMCACHED_SERVERS=%s-memcached:11211" % config.project_name)
        services[config.project_name]['depends_on'].append("%s-memcached" % config.project_name)

      if with_redis:
        services["%s-redis" % config.project_name] = {
          'image': 'redis:3.2-alpine'
        }
        if compose_environment == 'development':
          services["%s-redis" % config.project_name]['ports'] = ["6379:6379"]
        services[config.project_name]['environment'].append("REDIS_URL=redis://%s-redis:6379/%d" % (config.project_name, idx))
        services[config.project_name]['depends_on'].append("%s-redis" % config.project_name)

      if with_mongodb:
        services["%s-mongodb" % config.project_name] = {
          'image': 'mongo:3.0',
          'command': 'mongod --smallfiles'
        }
        if compose_environment == 'development':
          services["%s-mongodb" % config.project_name]['ports'] = ["27017:27017"]
        services[config.project_name]['environment'].append("MONGO_URL=mongodb://%s-mongodb:27017/%s" % (config.project_name, compose_environment))
        services[config.project_name]['depends_on'].append("%s-mongodb" % config.project_name)

      if with_postgres:
        services["%s-postgres" % config.project_name] = {
          'image': 'postgres:9.4'
        }
        if compose_environment == 'development':
          services["%s-postgres" % config.project_name]['ports'] = ["5432:5432"]
        services[config.project_name]['environment'].append("DATABASE_URL=postgresql://%s-postgres/%s" % (config.project_name, compose_environment))
        services[config.project_name]['depends_on'].append("%s-postgres" % config.project_name)

      if with_rabbitmq:
        services["%s-rabbitmq" % config.project_name] = {
          'image': 'rabbitmq:3.6-management-alpine'
        }
        if compose_environment == 'development':
          services["%s-rabbitmq" % config.project_name]['ports'] = ["5672:5672","15672:15672"]
        services[config.project_name]['environment'].append("RABBITMQ_URL=amqp://%s-rabbitmq/%s" % (config.project_name, urllib.quote_plus('/')))
        services[config.project_name]['depends_on'].append("%s-rabbitmq" % config.project_name)

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
        environment.append({'name': 'REDIS_URL', 'value': "redis://%s-redis:6379" % config.project_name})
      if with_mongodb:
        environment.append({'name': 'MONGO_URL', 'value': "mongodb://%s-mongodb:27017" % config.project_name})
      if with_postgres:
        environment.append({'name': 'DATABASE_URL', 'value': "postgresql://%s-postgres/%s" % (config.project_name, stack)})
      if with_rabbitmq:
        environment.append({'name': 'RABBITMQ_URL', 'value': "amqp://%s-rabbitmq/%s" % (config.project_name, urllib.quote_plus('/'))})

      if stack == 'production':
        replicas = 2
      else:
        replicas = 1

      deployment_data = build_deployment(config.project_name,
                                          "%s:%s" % (config.aws_ecr_registry, stack),
                                          port, environment=environment, always_pull=True, replicas=replicas)

      service_data = build_service(config.project_name, port, target_port=port, internal=False)

      stack_yaml = deployment_data + service_data

      if with_memcached:
        stack_yaml += build_deployment(config.project_name, 'memcached:1.4', 11211, layer='database', component='memcached')
        stack_yaml += build_service(config.project_name, 11211, layer='database', component='memcached')

      if with_redis:
        stack_yaml += build_deployment(config.project_name, 'redis:3.2-alpine', 6379, layer='database', component='redis')
        stack_yaml += build_service(config.project_name, 6379, layer='database', component='redis')

      if with_mongodb:
        stack_yaml += build_deployment(config.project_name, 'mongodb:3.0', 27017, layer='database', component='mongodb')
        stack_yaml += build_service(config.project_name, 27017, layer='database', component='mongodb')

      if with_postgres:
        stack_yaml += build_deployment(config.project_name, 'postgres:9.4', 5432, layer='database', component='postgres')
        stack_yaml += build_service(config.project_name, 5432, layer='database', component='postgres')

      if with_rabbitmq:
        stack_yaml += build_deployment(config.project_name, 'rabbitmq:3.6-management-alpine', 5672, layer='messaging', component='rabbitmq')
        stack_yaml += build_service(config.project_name, 5672, layer='messaging', component='rabbitmq')

      f.write(stack_yaml)

  print_green("Config created in ./hokusai")

  ecr = ECR()
  if ecr.project_repository_exists():
    print_green("ECR repository %s found. Skipping creation." % config.project_name)
    return 0

  if ecr.create_project_repository():
    print_green("Created ECR repository %s" % config.project_name)
    return 0
  else:
    print_red("Could not create ECR repository %s - check your credentials." % config.project_name)
    return 1
