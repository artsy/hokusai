import sys
from functools import wraps

from hokusai.lib.common import print_red, CalledProcessError

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
      if e.output is not None:
        print_red("ERROR: %s" % e.output)
      sys.exit(-1)
    except Exception, e:
      if hasattr(e, 'message'):
        print_red("ERROR: %s" % e.message)
      sys.exit(-1)
  return wrapper
