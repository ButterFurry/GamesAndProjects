# -*- mode: python ; coding: utf-8 -*-

import os

# Define the path to the 'src' directory in the parent directory
src_path = os.path.abspath(os.path.join('..', 'src'))

# Define the path for the output directories in the parent directory
output_dir = os.path.abspath('..')

a = Analysis(
    [os.path.join(src_path, 'app.py')],
    pathex=[src_path],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)
splash = Splash(
    'splash.png',
    binaries=a.binaries,
    datas=a.datas,
    text_pos=None,
    text_size=12,
    minify_script=True,
    always_on_top=True,
)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    splash,
    splash.binaries,
    [],
    name='DOTTiE',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=output_dir,  # Set runtime_tmpdir to the parent directory
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
