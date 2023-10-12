# -*- coding: utf-8 -*-

import os
import platform
import random
import re
import shutil
import signal
import string
import tempfile

from botocore import session as botosession
from datetime import datetime
from pathlib import Path
from subprocess import (
  call, check_call, check_output, Popen, STDOUT
)
from termcolor import cprint
from urllib.parse import urlparse

from hokusai.lib.config import config
from hokusai.lib.exceptions import (
  CalledProcessError, HokusaiError
)
from hokusai.services.s3 import S3Interface


CONTEXT_SETTINGS = {
  'terminal_width': 10000,
  'max_content_width': 10000,
  'help_option_names': ['-h', '--help']
}

EXIT_SIGNALS = [signal.SIGHUP, signal.SIGINT, signal.SIGQUIT, signal.SIGPIPE, signal.SIGTERM]

VERBOSE = False

AWS_DEFAULT_REGION = 'us-east-1'

def clean_string(str):
  return str.lower().replace('_', '-')

def get_platform():
  ''' get the platform (e.g. darwin, linux) of the machine '''
  return platform.system().lower()

def get_region_name():
  # boto3 autodiscovery
  _region = botosession.get_session().get_config_variable('region')
  if _region:
    return _region
  # boto2 compatibility
  if os.environ.get('AWS_REGION'):
    return os.environ.get('AWS_REGION')
  return AWS_DEFAULT_REGION

def get_verbosity():
  global VERBOSE
  return VERBOSE

def k8s_uuid():
  uuid = []
  for i in range(0,5):
    uuid.append(random.choice(string.ascii_lowercase))
  return ''.join(uuid)

def local_to_local(
  source_path,
  target_dir,
  target_file,
  create_target_dir=True,
  mode=0o660
):
  '''
  copy source file to target dir/file
  optionally create target dir, set target file mode as desired
  0o660 = rw-rw---- (read/write by file owner or group owner)
  '''
  # expand any ~
  expanded_target_dir = os.path.expanduser(target_dir)

  target_path = os.path.join(expanded_target_dir, target_file)
  target_path_obj = Path(target_path)

  # raise if target exists and is a dir
  if target_path_obj.is_dir():
    raise HokusaiError(f'Target {target_path} is an existing directory!')

  # if target exists and is a file, back it up
  if target_path_obj.is_file():
    backup_path = f'{target_path}.backup.{utc_yyyymmdd()}'
    shutil.copyfile(target_path, backup_path)

  # if target dir does not exist, create it if desired
  if create_target_dir:
    target_dir_obj = Path(expanded_target_dir)
    # noop if dir exists, error if what exists is a file
    target_dir_obj.mkdir(parents=True, exist_ok=True)

  shutil.copyfile(source_path, target_path)
  os.chmod(target_path, mode)

def pick_no():
  return random.choice(["Nope", "No", "нет", "Ne", "नहीं", "Daabi", "Nein", "Nay", "Nē", "ні", "خیر", "Nie", "Non", "ניט", "не", "아니", "いや", "没有", "Não"])

def pick_yes():
  return random.choice(["Yep", "Si", "да", "Da", "Aane", "हाँ", "Ja", "はい", "Jā", "так", "بله", "Tak", "Wi", "Oui", "יאָ", "예", "是", "Sim"])

def print_green(msg, newline_before=False, newline_after=False):
  cprint(smart_str(msg, newline_before, newline_after), 'green')

def print_red(msg, newline_before=False, newline_after=False):
  cprint(smart_str(msg, newline_before, newline_after), 'red')

def print_smart(msg, newline_before=False, newline_after=False):
  print(smart_str(msg, newline_before, newline_after))

def print_yellow(msg, newline_before=False, newline_after=False):
  cprint(smart_str(msg, newline_before, newline_after), 'yellow')

def set_verbosity(v):
  global VERBOSE
  VERBOSE = v or config.always_verbose

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

def uri_to_local(uri, target_dir, target_file):
  '''
  copy file from uri to target_dir/target_file
  support s3 scheme uri: s3://bucket/key
  support no scheme uri (i.e. local file): /path/to/file, ./path/to/file
  '''
  parsed_uri = urlparse(uri)
  tmpdir = tempfile.mkdtemp()
  try:
    if parsed_uri.scheme == 's3':
      s3_interface = S3Interface()
      filename = 'downloaded_file'
      file_path = os.path.join(tmpdir, filename)
      s3_interface.download(uri, file_path)
      local_to_local(file_path, target_dir, target_file)
    elif parsed_uri.scheme == '':
      local_to_local(parsed_uri.path, target_dir, target_file)
    else:
      raise HokusaiError(f'URI {uri} has unsupported scheme. Only "s3://" and file paths are supported.')
  except:
    print_red(
      f'Error: failed to copy {uri} to {os.path.join(target_dir, target_file)}'
    )
    raise
  finally:
    shutil.rmtree(tmpdir)

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

def utc_yyyymmdd():
  '''
  return yymmdd (utc), example:
  for January 15th, 1999, return 19990115
  '''
  return datetime.utcnow().strftime("%Y%m%d")

def validate_key_value(key_value):
  ''' raise if key_value is NOT of the form KEY=VALUE '''
  if '=' not in key_value:
    raise HokusaiError(
      "Error: key/value pair must be of the form 'KEY=VALUE'"
    )

def verbose(msg, mask=()):
  if VERBOSE:
    if mask:
      print_yellow("==> hokusai exec `%s`" % re.sub(mask[0], mask[1], msg), newline_after=True)
    else:
      print_yellow("==> hokusai exec `%s`" % msg, newline_after=True)
  return msg
