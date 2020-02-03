# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['nfdiag.py'],
             pathex=['/Users/david/Documents/PycharmProjects/nCipher_Logs'],
             binaries=[],
             datas=[('enquiry.json', '.'), ('dictionary.json', '.'), ('fips.json', '.'), ('nfkminfo.json', '.')],
             hiddenimports=[],
             hookspath=[],
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
          name='nfdiag',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True , icon='solo.icns')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='nfdiag')
