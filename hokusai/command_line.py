import sys
import os
from hokusai.cli import *

if getattr(sys, 'frozen', False):
    os.environ['SSL_CERT_FILE'] = os.path.join(sys._MEIPASS, 'lib', 'cert.pem')

def main():
  base(obj={})
