import sys

from contextlib import contextmanager
from StringIO import StringIO

from functools import wraps

import mock

from hokusai import common

@contextmanager
def captured_output():
  new_out, new_err = StringIO(), StringIO()
  old_out, old_err = sys.stdout, sys.stderr
  try:
    sys.stdout, sys.stderr = new_out, new_err
    yield sys.stdout, sys.stderr
  finally:
    sys.stdout, sys.stderr = old_out, old_err

def mocked_subprocess(func=None, retval='mocked!', retcode=0):
	def _decorate(function):
		@wraps(function)
		def wrapper(*args, **kwargs):
		  _subprocess_call = common.call
		  _subprocess_check_call = common.check_call
		  _subprocess_check_output = common.check_output
		  try:
		    common.call = mock.create_autospec(common.call, return_value=retcode)
		    common.check_call = mock.create_autospec(common.check_call, return_value=retcode)
		    common.check_output = mock.create_autospec(common.check_output, return_value=retval)
		    return function(*args, **kwargs)
		  finally:
		    common.call = _subprocess_call
		    common.check_call = _subprocess_check_call
		    common.check_output = _subprocess_check_output
		return wrapper
	if func:
		return _decorate(func)
	return _decorate
