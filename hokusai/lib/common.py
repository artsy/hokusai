# -*- coding: utf-8 -*-

import os
import sys
import signal
import string
import random
import json
import re

from subprocess import call, check_call, check_output, Popen, STDOUT

import yaml

from botocore import session as botosession

from termcolor import cprint

from hokusai.lib.config import config
from hokusai.lib.exceptions import CalledProcessError

CONTEXT_SETTINGS = {
  'terminal_width': 10000,
  'max_content_width': 10000,
  'help_option_names': ['-h', '--help']
}

EXIT_SIGNALS = [signal.SIGHUP, signal.SIGINT, signal.SIGQUIT, signal.SIGPIPE, signal.SIGTERM]

VERBOSE = False

AWS_DEFAULT_REGION = 'us-east-1'

def smart_str(s, newline_before=False, newline_after=False):
  if newline_before:
    s = '\n' + s
  if newline_after:
    s = s + '\n'
  if sys.version_info[0] >= 3:
    if isinstance(s, bytes):
      return s.decode('utf-8')
  else:
    if isinstance(s, unicode):
      return s.encode('utf-8')
  if isinstance(s, int) or isinstance(s, float):
      return str(s)
  return s

def print_smart(msg, newline_before=False, newline_after=False):
  print(smart_str(msg, newline_before, newline_after))

def print_green(msg, newline_before=False, newline_after=False):
  cprint(smart_str(msg, newline_before, newline_after), 'green')

def print_red(msg, newline_before=False, newline_after=False):
  cprint(smart_str(msg, newline_before, newline_after), 'red')

def print_yellow(msg, newline_before=False, newline_after=False):
  cprint(smart_str(msg, newline_before, newline_after), 'yellow')

def set_verbosity(v):
  global VERBOSE
  VERBOSE = v or config.always_verbose

def get_verbosity():
  global VERBOSE
  return VERBOSE

def verbose(msg, mask=()):
  if VERBOSE:
    if mask:
      print_yellow("==> hokusai exec `%s`" % re.sub(mask[0], mask[1], msg), newline_after=True)
    else:
      print_yellow("==> hokusai exec `%s`" % msg, newline_after=True)
  return msg

def returncode(command, mask=()):
  return call(verbose(command, mask=mask), stderr=STDOUT, shell=True)

def shout(command, print_output=False, mask=()):
  try:
    if print_output:
      return check_call(verbose(command, mask=mask), stderr=STDOUT, shell=True)
    else:
      retval = check_output(verbose(command, mask=mask), stderr=STDOUT, shell=True)
      if str == bytes:
        # Python 2
        return retval
      else:
        # Python 3
        if type(retval) == bytes:
          return retval.decode('utf-8')
        else:
          return retval

  except CalledProcessError as e:
    if mask:
      if hasattr(e, 'cmd') and e.cmd is not None:
        if str == bytes:
          # Python 2
          cmd = re.sub(mask[0], mask[1], e.cmd)
        else:
          # Python 3
          if type(e.cmd) == bytes:
            cmd = re.sub(mask[0], mask[1], e.cmd.decode('utf-8'))
          else:
            cmd = re.sub(mask[0], mask[1], e.cmd)
        e.cmd = cmd
      if hasattr(e, 'output') and e.output is not None:
        if str == bytes:
          # Python 2
          output = re.sub(mask[0], mask[1], e.output)
        else:
          # Python 3
          if type(e.output) == bytes:
            output = re.sub(mask[0], mask[1], e.output.decode('utf-8'))
          else:
            output = re.sub(mask[0], mask[1], e.output)
        e.output = output
    raise

def shout_concurrent(commands, print_output=False, mask=()):
  if print_output:
    processes = [Popen(verbose(command, mask=mask), shell=True) for command in commands]
  else:
    processes = [Popen(verbose(command, mask=mask), shell=True, stdout=open(os.devnull, 'w'), stderr=STDOUT) for command in commands]

  return_codes = []
  try:
    for p in processes:
      return_codes.append(p.wait())
  except KeyboardInterrupt:
    for p in processes:
      p.terminate()
    return_codes = [1 for p in processes]
  return return_codes

def k8s_uuid():
  uuid = []
  for i in range(0,5):
    uuid.append(random.choice(string.ascii_lowercase))
  return ''.join(uuid)

def clean_string(str):
  return str.lower().replace('_', '-')

def get_region_name():
  # boto3 autodiscovery
  _region = botosession.get_session().get_config_variable('region')
  if _region:
    return _region
  # boto2 compatibility
  if os.environ.get('AWS_REGION'):
    return os.environ.get('AWS_REGION')
  return AWS_DEFAULT_REGION

def pick_yes():
  return random.choice(["Yep", "Si", "да", "Da", "Aane", "हाँ", "Ja", "はい", "Jā", "так", "بله", "Tak", "Wi", "Oui", "יאָ", "예", "是", "Sim"])

def pick_no():
  return random.choice(["Nope", "No", "нет", "Ne", "नहीं", "Daabi", "Nein", "Nay", "Nē", "ні", "خیر", "Nie", "Non", "ניט", "не", "아니", "いや", "没有", "Não"])
