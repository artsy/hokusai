import os

from hokusai import CWD
from hokusai.lib import config


config.HOKUSAI_CONFIG_FILE = os.path.join(CWD, 'test/fixtures/project/hokusai/', 'config.yml')
