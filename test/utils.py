import sys
from contextlib import contextmanager
from io import StringIO
from hokusai.lib.common import get_verbosity, set_verbosity

@contextmanager
def captured_output():
  new_out, new_err = StringIO(), StringIO()
  old_out, old_err = sys.stdout, sys.stderr
  try:
    sys.stdout, sys.stderr = new_out, new_err
    yield sys.stdout, sys.stderr
  finally:
    sys.stdout, sys.stderr = old_out, old_err

@contextmanager
def mock_verbosity(verbosity):
  old_verbosity = get_verbosity()

  set_verbosity(verbosity)
  yield
  set_verbosity(old_verbosity)
