import os

from hokusai.services.docker import Docker

def build(filename):
  Docker().build(filename=filename)
