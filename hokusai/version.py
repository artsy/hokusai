VERSION = 'v0.0.0'

try:
  from ._version import version
  VERSION = version
except ImportError:
  pass
