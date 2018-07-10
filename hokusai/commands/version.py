import os

from hokusai.lib.command import command
from hokusai.lib.common import print_green
from hokusai.version import VERSION

@command
def version():
  print_green(VERSION)
