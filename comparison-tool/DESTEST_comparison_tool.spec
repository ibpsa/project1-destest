# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['DESTEST_comparison_tool.py'],
             pathex=['D:\\GIT\\project1-destest\\comparison-tool'],
             binaries=[],
#             datas=[],
#             datas=[("D:\\Programme\\Anaconda\\envs\\uesgraphs_adv\\Lib\\site-packages\\plotly\\", "plotly")],
             datas=[("c:\\Python37\\lib\\site-packages\\PyInstaller\\plotly\\", "plotly")],
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
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='DESTEST_comparison_tool',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True )
