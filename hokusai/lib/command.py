import sys
import traceback
from functools import wraps

from hokusai.lib.common import print_red, get_verbosity
from hokusai.lib.exceptions import CalledProcessError, HokusaiError

def command(func):
  @wraps(func)
  def wrapper(*args, **kwargs):
    try:
      result = func(*args, **kwargs)
      if result is None:
        sys.exit(0)
      else:
        sys.exit(result)
    except HokusaiError as e:
      print_red(e.message)
      sys.exit(e.return_code)
    except SystemExit:
      raise
    except KeyboardInterrupt:
      raise
    except (CalledProcessError, Exception) as e:
      if get_verbosity():
        print_red(traceback.format_exc(e))
      else:
        print_red("ERROR: %s" % str(e))
      sys.exit(-1)
  return wrapper
