# -*- mode: python -*-

block_cipher = None


a = Analysis(['chronotherium/main.py'],
             pathex=['./chronotherium', './clubsandwich'],
             binaries=[('shared/libBearLibTerminal.so', '.')],
      	     datas=[('./resources/VeraMono.ttf', '.'),
                    ('./resources/ttf-symbola/Symbola.ttf', '.'),
                    ('./resources/symbola_codepage.txt', '.')],
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
          name='chronotherium',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True )
