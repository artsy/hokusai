import os
import signal

from hokusai.lib.config import HOKUSAI_CONFIG_DIR, DEVELOPMENT_YML_FILE, config
from hokusai.lib.common import print_green, shout, EXIT_SIGNALS
from hokusai.services.docker import Docker
from hokusai.lib.docker_compose_helpers import generate_compose_command, get_yaml_template


def dev_start(build, detach, filename):
  compose_command = generate_compose_command(filename, default_yaml_file=DEVELOPMENT_YML_FILE)
  def cleanup(*args):
    shout(
      f'{compose_command} -p hokusai stop',
      print_output=True
    )
  for sig in EXIT_SIGNALS:
    signal.signal(sig, cleanup)
  opts = ''
  if build:
    yaml_template = get_yaml_template(filename, default_yaml_file=DEVELOPMENT_YML_FILE)
    Docker().build(filename=yaml_template)
  if detach:
    opts += ' -d'
  if not detach:
    print_green("Starting development environment... Press Ctrl+C to stop.")
  shout(
    f'{compose_command} -p hokusai up{opts}',
    print_output=True
  )
  if detach:
    print_green("Run `hokousai dev stop` to shut down, or `hokusai dev logs --follow` to tail output.")

def dev_stop(filename):
  compose_command = generate_compose_command(filename, default_yaml_file=DEVELOPMENT_YML_FILE)
  shout(
    f'{compose_command} -p hokusai stop',
    print_output=True
  )

def dev_status(filename):
  compose_command = generate_compose_command(filename, default_yaml_file=DEVELOPMENT_YML_FILE)
  shout(
    f'{compose_command} -p hokusai ps',
    print_output=True
  )

def dev_logs(follow, tail, filename):
  compose_command = generate_compose_command(filename, default_yaml_file=DEVELOPMENT_YML_FILE)
  opts = ''
  if follow:
    opts += ' --follow'
  if tail:
    opts += " --tail=%i" % tail
  shout(
    f'{compose_command} -p hokusai logs{opts}',
    print_output=True
  )

def dev_run(container_command, service_name, stop, filename):
  compose_command = generate_compose_command(filename, default_yaml_file=DEVELOPMENT_YML_FILE)
  if service_name is None:
    service_name = config.project_name
  shout(
    f'{compose_command} -p hokusai run {service_name} {container_command}',
    print_output=True
  )
  if stop:
    shout(
      f'{compose_command} -p hokusai stop',
      print_output=True
    )

def dev_clean(filename):
  compose_command = generate_compose_command(filename, default_yaml_file=DEVELOPMENT_YML_FILE)
  shout(
    f'{compose_command} -p hokusai stop',
    print_output=True
  )
  shout(
    f'{compose_command} -p hokusai rm --force',
    print_output=True
  )
