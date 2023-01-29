# -*- mode: python ; coding: utf-8 -*-

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
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='hokusai',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='hokusai')
