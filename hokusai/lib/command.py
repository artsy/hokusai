import sys
import traceback
from functools import wraps

from hokusai.lib.common import print_red, CalledProcessError, get_verbosity

def command(func):
  @wraps(func)
  def wrapper(*args, **kwargs):
    try:
      result = func(*args, **kwargs)
      if result is None:
        sys.exit(0)
      else:
        sys.exit(result)
    except SystemExit:
      raise
    except KeyboardInterrupt:
      raise
    except CalledProcessError, e:
      if get_verbosity():
        print_red(traceback.format_exc(e))
      else:
        print_red("ERROR: %s" % str(e))
      sys.exit(-1)
    except Exception, e:
      if get_verbosity():
        print_red(traceback.format_exc(e))
      else:
        print_red("ERROR: %s" % str(e))
      sys.exit(-1)
  return wrapper
