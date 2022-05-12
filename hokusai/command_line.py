import sys
import os

from hokusai.cli import *
from hokusai.lib.environment import cert_file_path

os.environ['SSL_CERT_FILE'] = cert_file_path()

def main():
  base(obj={})
