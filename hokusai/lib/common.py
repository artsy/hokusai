import os
import sys
import signal
import string
import random
import json


from subprocess import call, check_call, check_output, Popen, STDOUT

import yaml
import boto3

from termcolor import cprint

from hokusai.lib.exceptions import CalledProcessError

CONTEXT_SETTINGS = {
  'terminal_width': 10000,
  'max_content_width': 10000,
  'help_option_names': ['-h', '--help']
}

EXIT_SIGNALS = [signal.SIGHUP, signal.SIGINT, signal.SIGQUIT, signal.SIGPIPE, signal.SIGTERM]

YAML_HEADER = '---\n'

VERBOSE = False

def print_green(msg):
  cprint(msg, 'green')

def print_red(msg):
  cprint(msg, 'red')

def set_verbosity(v):
  global VERBOSE
  VERBOSE = v

def get_verbosity():
  global VERBOSE
  return VERBOSE

def verbose(msg):
  if VERBOSE: cprint("==> hokusai exec `%s`" % msg, 'yellow')
  return msg


def returncode(command):
  return call(verbose(command), stderr=STDOUT, shell=True)

def shout(command, print_output=False):
  if print_output:
    return check_call(verbose(command), stderr=STDOUT, shell=True)
  else:
    return check_output(verbose(command), stderr=STDOUT, shell=True)

def shout_concurrent(commands, print_output=False):
  if print_output:
    processes = [Popen(verbose(command), shell=True) for command in commands]
  else:
    processes = [Popen(verbose(command), shell=True, stdout=open(os.devnull, 'w'), stderr=STDOUT) for command in commands]

  return_codes = []
  try:
    for p in processes:
      return_codes.append(p.wait())
  except KeyboardInterrupt:
    for p in processes:
      p.terminate()
      return -1

  for return_code in return_codes:
    if return_code:
      return return_code

def k8s_uuid():
  uuid = []
  for i in range(0,5):
    uuid.append(random.choice(string.lowercase))
  return ''.join(uuid)

def clean_string(str):
  return str.lower().replace('_', '-')
