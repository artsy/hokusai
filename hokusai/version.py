import os

with open(os.path.join(os.path.dirname(__file__), "VERSION")) as f:
  VERSION = f.read().strip()
