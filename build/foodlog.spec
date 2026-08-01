# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec file for FoodLog."""

import sys
from pathlib import Path

entry_point = 'main.py'
output_name = 'foodlog_win' if sys.platform == 'win32' else 'foodlog_linux'
icon_path = 'build/foodlog.ico' if Path('build/foodlog.ico').exists() else None

a = Analysis(
    [entry_point],
    pathex=['src'],
    binaries=[],
    datas=[],
    hiddenimports=[
        'tkinter',
        'sqlite3',
        'matplotlib',
        'matplotlib.backends.backend_tkagg',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludedimports=[],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name=output_name,
    icon=icon_path,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
