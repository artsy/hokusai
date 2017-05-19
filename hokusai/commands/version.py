import os

from hokusai.lib.command import command
from hokusai.lib.common import print_green

@command
def version():
  version_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.pardir, 'VERSION.txt')
  print_green(open(version_file, 'r').read())
