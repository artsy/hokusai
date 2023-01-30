try:
  from hokusai._version import version
  VERSION = version
except ImportError:
  VERSION = 'v0.0.0'
  pass
