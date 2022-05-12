import os

from hokusai.lib.environment import version_file_path

with open(version_file_path()) as f:
  VERSION = f.read().strip()
