import os
import signal

HOKUSAI_CONFIG_FILE = os.path.join(os.getcwd(), 'hokusai', 'config.yml')

EXIT_SIGNALS = [signal.SIGHUP, signal.SIGINT, signal.SIGQUIT, signal.SIGPIPE, signal.SIGTERM]

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

YAML_HEADER = '---\n'

def print_green(msg):
  print(GREEN + msg + NC)

def print_red(msg):
  print(RED + msg + NC)
