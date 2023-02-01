# -*- mode: python -*-

import platform

if platform.system() == "Darwin":
  from PyInstaller.utils.hooks import exec_statement
  cert_datas = exec_statement("""
      import ssl
      print(ssl.get_default_verify_paths().cafile)""").strip().split()
  cert_datas = [(f, 'lib') for f in cert_datas]
else:
  cert_datas = []

block_cipher = None

import sys
hidden_imports = ['configparser']

a = Analysis(['bin/hokusai'],
             pathex=['.'],
             binaries=[],
             datas=[('./hokusai/templates/*.j2', 'hokusai_datas/templates/'), ('./hokusai/templates/.dockerignore.j2', 'hokusai_datas/templates/'), ('./hokusai/templates/hokusai/*.j2', 'hokusai_datas/templates/hokusai/')] + cert_datas,
             hiddenimports=hidden_imports,
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='hokusai',
          debug=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True )
