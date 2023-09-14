import sys
import os

from hokusai.cli import *
from hokusai.lib.environment import cert_file_path

if cert_file_path() is not None:
  os.environ['SSL_CERT_FILE'] = cert_file_path()

def main():
  base(obj={})
