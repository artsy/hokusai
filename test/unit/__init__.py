import os

# must be set before importing any hokusai module
os.environ['HOME'] = os.path.join(os.getcwd(), 'test/fixtures/user')

from hokusai import CWD
from hokusai.lib import config

config.HOKUSAI_CONFIG_FILE = os.path.join(CWD, 'test/fixtures/project/hokusai/', 'config.yml')
