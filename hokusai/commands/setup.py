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
from hokusai.lib.common import print_green, build_service, build_deployment, YAML_HEADER
from hokusai.lib.exceptions import HokusaiError

@command
def setup(aws_account_id, project_type, project_name, aws_ecr_region, port):

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
      'production': [{'name': 'RACK_ENV', 'value': 'production'}]
    }

  elif project_type == 'ruby-rails':
    dockerfile = env.get_template("Dockerfile-rails.j2")
    base_image = 'ruby:latest'
    run_command = 'bundle exec rails server'
    development_command = 'bundle exec rails server'
    test_command = 'bundle exec rake'
    runtime_environment = {
      'development': ["RAILS_ENV=development"],
      'test': ["RAILS_ENV=test"],
      'production': [{'name': 'RAILS_ENV', 'value': 'production'},
                      {'name': 'RAILS_SERVE_STATIC_FILES', 'value': 'true'},
                      {'name': 'RAILS_LOG_TO_STDOUT', 'value': 'true'}]
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
      'production': [{'name': 'MIX_ENV', 'value': 'prod'}]
    }

  elif project_type == 'python-wsgi':
    dockerfile = env.get_template("Dockerfile-python.j2")
    base_image = 'python:latest'
    run_command = "gunicorn -b 0.0.0.0:%s app" % port
    development_command = "python -m werkzeug.serving -b 0.0.0.0:%s %s" % (port, project_name)
    test_command = 'python -m unittest discover .'
    runtime_environment = {
      'development': ["CONFIG_FILE=config/development.py"],
      'test': ["CONFIG_FILE=config/test.py"],
      'production': [{'name': 'CONFIG_FILE', 'value': 'config/production.py'}]
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

  for compose_environment in ['development', 'test']:
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

      data = OrderedDict([
        ('version', '2'),
        ('services', services)
      ])
      payload = YAML_HEADER + yaml.safe_dump(data, default_flow_style=False)
      f.write(payload)

  for stack in ['staging', 'production']:
    with open(os.path.join(os.getcwd(), 'hokusai', "%s.yml" % stack), 'w') as f:
      if stack == 'production':
        replicas = 2
      else:
        replicas = 1

      deployment_data = build_deployment(config.project_name,
                                          "%s:%s" % (config.aws_ecr_registry, stack),
                                          port, environment=runtime_environment['production'], always_pull=True, replicas=replicas)

      service_data = build_service(config.project_name, port, target_port=port, internal=False)

      stack_yaml = deployment_data + service_data

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
    raise HokusaiError("Could not create ECR repository %s - check your credentials." % config.project_name)
