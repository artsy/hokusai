import os
import signal

from hokusai import CWD
from hokusai.lib.command import command
from hokusai.lib.config import HOKUSAI_CONFIG_DIR, DEVELOPMENT_YML_FILE, config
from hokusai.lib.common import print_green, shout, EXIT_SIGNALS
from hokusai.lib.exceptions import HokusaiError
from hokusai.services.docker import Docker
from hokusai.lib.template_selector import TemplateSelector
from hokusai.lib.docker_compose_helpers import follow_extends
from hokusai.services.yaml_spec import YamlSpec

@command()
def dev_start(build, detach, filename):
  if filename is None:
    yaml_template = TemplateSelector().get(os.path.join(CWD, HOKUSAI_CONFIG_DIR, DEVELOPMENT_YML_FILE))
  else:
    yaml_template = TemplateSelector().get(filename)

  docker_compose_yml = YamlSpec(yaml_template).to_file()
  follow_extends(docker_compose_yml)

  def cleanup(*args):
    shout("docker-compose -f %s -p hokusai stop" % docker_compose_yml, print_output=True)
  for sig in EXIT_SIGNALS:
    signal.signal(sig, cleanup)

  opts = ''
  if build:
    Docker().build(filename=yaml_template)
  if detach:
    opts += ' -d'

  if not detach:
    print_green("Starting development environment... Press Ctrl+C to stop.")

  shout("docker-compose -f %s -p hokusai up%s" % (docker_compose_yml, opts), print_output=True)

  if detach:
    print_green("Run `hokousai dev stop` to shut down, or `hokusai dev logs --follow` to tail output.")

@command()
def dev_stop(filename):
  if filename is None:
    yaml_template = TemplateSelector().get(os.path.join(CWD, HOKUSAI_CONFIG_DIR, DEVELOPMENT_YML_FILE))
  else:
    yaml_template = TemplateSelector().get(filename)

  docker_compose_yml = YamlSpec(yaml_template).to_file()
  follow_extends(docker_compose_yml)

  shout("docker-compose -f %s -p hokusai stop" % docker_compose_yml, print_output=True)

@command()
def dev_status(filename):
  if filename is None:
    yaml_template = TemplateSelector().get(os.path.join(CWD, HOKUSAI_CONFIG_DIR, DEVELOPMENT_YML_FILE))
  else:
    yaml_template = TemplateSelector().get(filename)

  docker_compose_yml = YamlSpec(yaml_template).to_file()
  follow_extends(docker_compose_yml)

  shout("docker-compose -f %s -p hokusai ps" % docker_compose_yml, print_output=True)

@command()
def dev_logs(follow, tail, filename):
  if filename is None:
    yaml_template = TemplateSelector().get(os.path.join(CWD, HOKUSAI_CONFIG_DIR, DEVELOPMENT_YML_FILE))
  else:
    yaml_template = TemplateSelector().get(filename)

  docker_compose_yml = YamlSpec(yaml_template).to_file()
  follow_extends(docker_compose_yml)

  opts = ''
  if follow:
    opts += ' --follow'
  if tail:
    opts += " --tail=%i" % tail

  shout("docker-compose -f %s -p hokusai logs%s" % (docker_compose_yml, opts), print_output=True)

@command()
def dev_run(command, service_name, stop, filename):
  if filename is None:
    yaml_template = TemplateSelector().get(os.path.join(CWD, HOKUSAI_CONFIG_DIR, DEVELOPMENT_YML_FILE))
  else:
    yaml_template = TemplateSelector().get(filename)

  docker_compose_yml = YamlSpec(yaml_template).to_file()
  follow_extends(docker_compose_yml)

  if service_name is None:
    service_name = config.project_name

  shout("docker-compose -f %s -p hokusai run %s %s" % (docker_compose_yml, service_name, command), print_output=True)

  if stop:
    shout("docker-compose -f %s -p hokusai stop" % docker_compose_yml, print_output=True)

@command()
def dev_clean(filename):
  if filename is None:
    yaml_template = TemplateSelector().get(os.path.join(CWD, HOKUSAI_CONFIG_DIR, DEVELOPMENT_YML_FILE))
  else:
    yaml_template = TemplateSelector().get(filename)

  docker_compose_yml = YamlSpec(yaml_template).to_file()
  follow_extends(docker_compose_yml)

  shout("docker-compose -f %s -p hokusai stop" % docker_compose_yml, print_output=True)
  shout("docker-compose -f %s -p hokusai rm --force" % docker_compose_yml, print_output=True)
