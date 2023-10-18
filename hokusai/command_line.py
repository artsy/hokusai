import sys
import os

from hokusai.cli import *
from hokusai.lib.environment import cert_file_path

path = cert_file_path()
if path is not None:
  os.environ['SSL_CERT_FILE'] = path

def main():
  base(obj={})
