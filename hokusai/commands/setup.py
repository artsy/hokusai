import os
import urllib

from distutils.dir_util import mkpath
from collections import OrderedDict

import yaml

from jinja2 import Environment, PackageLoader, FileSystemLoader

from hokusai.lib.command import command
from hokusai.lib.config import config
from hokusai.services.ecr import ECR
from hokusai.lib.common import print_green, YAML_HEADER
from hokusai.lib.exceptions import HokusaiError

@command
def setup(aws_account_id, project_type, project_name, aws_ecr_region, port, internal, template_dir):
  if template_dir:
    env = Environment(loader=FileSystemLoader(template_dir))
  else:
    env = Environment(loader=PackageLoader('hokusai', 'templates'))

  mkpath(os.path.join(os.getcwd(), 'hokusai'))

  config.create(project_name.lower().replace('_', '-'), aws_account_id, aws_ecr_region)

  if project_type == 'ruby-rack':
    dockerfile = env.get_template("Dockerfile-ruby.j2")
    base_image = 'ruby:latest'
    run_command = 'bundle exec rackup'
    development_command = 'bundle exec rackup'
    test_command = 'bundle exec rake'
    runtime_environment = {
      'development': {"RACK_ENV": "development"},
      'test': {"RACK_ENV": "test"},
      'production': {'RACK_ENV': 'production'}
    }

  elif project_type == 'ruby-rails':
    dockerfile = env.get_template("Dockerfile-rails.j2")
    base_image = 'ruby:latest'
    run_command = 'bundle exec rails server'
    development_command = 'bundle exec rails server'
    test_command = 'bundle exec rake'
    runtime_environment = {
      'development': {"RAILS_ENV": "development"},
      'test': {"RAILS_ENV": "test"},
      'production': {'RAILS_ENV': 'production',
                     'RAILS_SERVE_STATIC_FILES': 'true',
                     'RAILS_LOG_TO_STDOUT': 'true'}
    }

  elif project_type == 'nodejs':
    dockerfile = env.get_template("Dockerfile-node.j2")
    base_image = 'node:latest'
    run_command = 'node index.js'
    development_command = 'node index.js'
    test_command = 'npm test'
    runtime_environment = {
      'development': {"NODE_ENV": "development"},
      'test': {"NODE_ENV": "test"},
      'production': {'NODE_ENV': 'production'}
    }

  elif project_type == 'elixir':
    dockerfile = env.get_template("Dockerfile-elixir.j2")
    base_image = 'elixir:latest'
    run_command = 'mix run --no-halt'
    development_command = 'mix run'
    test_command = 'mix test'
    runtime_environment = {
      'development': {"MIX_ENV": "dev"},
      'test': {'MIX_ENV': 'test'},
      'production': {'MIX_ENV': 'prod'}
    }

  elif project_type == 'python-wsgi':
    dockerfile = env.get_template("Dockerfile-python.j2")
    base_image = 'python:latest'
    run_command = "gunicorn -b 0.0.0.0:%s app" % port
    development_command = "python -m werkzeug.serving -b 0.0.0.0:%s %s" % (port, project_name)
    test_command = 'python -m unittest discover .'
    runtime_environment = {
      'development': {"CONFIG_FILE": "config/development.py"},
      'test': {"CONFIG_FILE": "config/test.py"},
      'production': {'CONFIG_FILE': 'config/production.py'}
    }

  with open(os.path.join(os.getcwd(), 'Dockerfile'), 'w') as f:
    f.write(dockerfile.render(base_image=base_image, command=run_command, target_port=port))

  with open(os.path.join(os.getcwd(), '.dockerignore'), 'w') as f:
    f.write(env.get_template("dockerignore.j2").render(project_type=project_type))

  with open(os.path.join(os.getcwd(), 'hokusai', "common.yml"), 'w') as f:
    f.write(env.get_template("common.yml.j2").render(project_name=config.project_name))

  with open(os.path.join(os.getcwd(), 'hokusai', "development.yml"), 'w') as f:
    f.write(env.get_template("development.yml.j2").render(
      project_name=config.project_name,
      development_command=development_command,
      port=port,
      environment=runtime_environment['development']
    ))
  with open(os.path.join(os.getcwd(), 'hokusai', "test.yml"), 'w') as f:
    f.write(env.get_template("test.yml.j2").render(
      project_name=config.project_name,
      development_command=test_command,
      environment=runtime_environment['test']
    ))
  with open(os.path.join(os.getcwd(), 'hokusai', "staging.yml"), 'w') as f:
    f.write(env.get_template("staging.yml.j2").render(
      project_name=config.project_name,
      component="web",
      port=port,
      layer="application",
      environment=runtime_environment['production'],
      image="%s:staging" % config.aws_ecr_registry,
      internal=internal
    ))
  with open(os.path.join(os.getcwd(), 'hokusai', "production.yml"), 'w') as f:
    f.write(env.get_template("production.yml.j2").render(
      project_name=config.project_name,
      component="web",
      port=port,
      layer="application",
      environment=runtime_environment['production'],
      image="%s:production" % config.aws_ecr_registry,
      internal=internal
    ))

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
