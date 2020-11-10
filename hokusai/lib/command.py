import os
import sys
import traceback
from functools import wraps

from hokusai.lib.common import print_red, get_verbosity
from hokusai.lib.exceptions import CalledProcessError, HokusaiError
from hokusai.lib.config import config

def command(config_check=True):
  def decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
      try:
        if config_check:
          config.check()
        result = func(*args, **kwargs)
        if result is None:
          sys.exit(0)
        else:
          sys.exit(result)
      except SystemExit:
        raise
      except KeyboardInterrupt:
        raise
      except HokusaiError as e:
        print_red("ERROR: %s" % e.message)
        sys.exit(e.return_code)
      except CalledProcessError as e:
        if get_verbosity() or os.environ.get('DEBUG'):
          print_red(traceback.format_exc())
        else:
          print_red("ERROR: %s" % str(e))
        if hasattr(e, 'output') and e.output is not None:
          if str == bytes:
            # Python 2
            print_red("ERROR: %s" % e.output)
          else:
            # Python 3
            if type(e.output) == bytes:
              print_red("ERROR: %s" % e.output.decode('utf-8'))
            else:
              print_red("ERROR: %s" % e.output)
        sys.exit(e.returncode)
      except Exception as e:
        if get_verbosity() or os.environ.get('DEBUG'):
          print_red(traceback.format_exc())
        else:
          print_red("ERROR: %s" % str(e))
        sys.exit(1)
    return wrapper
  return decorator
