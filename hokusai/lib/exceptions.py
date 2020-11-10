import re

from subprocess import CalledProcessError

class HokusaiError(Exception):
  def __init__(self, message, return_code=1, mask=()):
    if mask:
      self.message = re.sub(mask[0], mask[1], message)
    else:
      self.message = message
    self.return_code = return_code
