# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules
import os

a = Analysis(
    ['desktop.py'],
    pathex=['backend'],
    binaries=[],
    datas=[('frontend/dist', 'frontend/dist')],
    hiddenimports=collect_submodules('uvicorn.protocols') + collect_submodules('uvicorn.lifespan') + ['webview.platforms.edgechromium'],
    hookspath=[], runtime_hooks=[], excludes=['tkinter'], noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name='StudyHub', debug=False,
          bootloader_ignore_signals=False, strip=False, upx=False, console=bool(os.environ.get('STUDYHUB_BUILD_CONSOLE')),
          icon='assets/studyhub.ico')
coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False, name='StudyHub')
