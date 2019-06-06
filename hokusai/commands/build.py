import os

from hokusai.lib.command import command
from hokusai.services.docker import Docker

@command()
def build(yaml_file_name):
  Docker().build(yaml_file_name)
