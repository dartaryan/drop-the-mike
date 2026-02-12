# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for DROP THE MIKE
Build with: pyinstaller drop_the_mike.spec
"""
import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Detect platform for icon
if sys.platform == 'win32':
    icon_file = 'icon.ico'
elif sys.platform == 'darwin':
    icon_file = 'icon.icns'
else:
    icon_file = None

block_cipher = None

a = Analysis(
    ['drop_the_mike.py'],
    pathex=[],
    binaries=[],
    datas=collect_data_files('customtkinter'),
    hiddenimports=collect_submodules('customtkinter'),
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,  # onedir mode
    name='DropTheMike',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # windowed mode
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_file if icon_file and os.path.exists(icon_file) else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='DropTheMike',
)

# macOS .app bundle
if sys.platform == 'darwin':
    app = BUNDLE(
        coll,
        name='DropTheMike.app',
        icon=icon_file if icon_file and os.path.exists(icon_file) else None,
        bundle_identifier='com.dartaryan.dropthemike',
        info_plist={
            'CFBundleShortVersionString': '1.0.0',
            'CFBundleName': 'DROP THE MIKE',
            'CFBundleDisplayName': 'DROP THE MIKE',
            'NSHighResolutionCapable': True,
        },
    )
