import sys
from functools import wraps

from hokusai.common import print_red, CalledProcessError

def command(func):
  @wraps(func)
  def wrapper(*args, **kwargs):
    try:
      retval = func(*args, **kwargs)
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
    if retval is None:
      sys.exit(0)
    else:
      sys.exit(retval)
  return wrapper
