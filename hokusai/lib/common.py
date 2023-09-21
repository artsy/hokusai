# -*- coding: utf-8 -*-

import os
import platform
import random
import re
import shutil
import signal
import string

from botocore import session as botosession
from subprocess import call, check_call, check_output, Popen, STDOUT
from termcolor import cprint
from urllib.parse import urlparse

from hokusai.lib.config import config
from hokusai.lib.exceptions import CalledProcessError, HokusaiError
from hokusai.services.s3 import s3_interface


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

  if isinstance(s, bytes):
    return s.decode('utf-8')
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

def verbose_print_green(msg, newline_before=False, newline_after=False):
  ''' print_green only if verbose '''
  if VERBOSE:
    print_green(msg, newline_before=False, newline_after=False)

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
      if type(retval) == bytes:
        return retval.decode('utf-8')
      else:
        return retval

  except CalledProcessError as e:
    if mask:
      if hasattr(e, 'cmd') and e.cmd is not None:
        if type(e.cmd) == bytes:
          cmd = re.sub(mask[0], mask[1], e.cmd.decode('utf-8'))
        else:
          cmd = re.sub(mask[0], mask[1], e.cmd)
        e.cmd = cmd
      if hasattr(e, 'output') and e.output is not None:
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

def user():
  ''' obtain user name from environment '''
  user = None
  if os.environ.get('USER') is not None:
    # The regex used for the validation of name is
    # '[a-z0-9]([-a-z0-9]*[a-z0-9])?'
    user = re.sub(
      "[^0-9a-z]+", "-", os.environ.get('USER').lower()
    )
  return user

def validate_key_value(key_value):
  ''' raise if key_value is NOT of the form KEY=VALUE '''
  if '=' not in key_value:
    raise HokusaiError(
      "Error: key/value pair must be of the form 'KEY=VALUE'"
    )

def get_platform():
  ''' get the platform (e.g. darwin, linux) of the machine '''
  return platform.system().lower()

def uri_to_local(uri, local_file_path):
  '''
  given a uri of a file, copy file to local_file_path
  uri currently supported: s3://, file://
  '''
  parsed_uri = urlparse(uri)

  try:
    if parsed_uri.scheme == 's3':
      s3_interface.download(uri, local_file_path)
    elif parsed_uri.scheme == 'file':
      if parsed_uri.path != local_file_path:
        shutil.copy(parsed_uri.path, local_file_path)
    else:
      raise HokusaiError("uri must have a scheme of 'file:///' or 's3://'")
  except:
    print_red(f'Error: failed to copy {uri} to {local_file_path}')
    raise
