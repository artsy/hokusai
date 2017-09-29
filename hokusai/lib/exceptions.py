from subprocess import CalledProcessError

class HokusaiError(Exception):
  def __init__(self, message, return_code=1):
    self.message = message
    self.return_code = return_code
