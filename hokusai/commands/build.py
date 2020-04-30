import os

from hokusai.lib.command import command
from hokusai.services.docker import Docker

@command()
def build(filename):
  Docker().build(filename=filename)
