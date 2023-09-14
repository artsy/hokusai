import os
import sys

import hokusai

# detect whether code is run from a PyInstaller-created bundle
# if is, support files are found in paths as coded in PyInstaller spec file (see 'datas' arg of Analysis() call)
def frozen():
  return getattr(sys, 'frozen', False)

def cert_file_path():
  if frozen():
    return sys._MEIPASS + '/lib/cert.pem'

def templates_dir_path():
  if frozen():
    return sys._MEIPASS + '/hokusai_datas/templates'
  else:
    return os.path.dirname(hokusai.__file__) + '/templates'
