# -*- mode: python ; coding: utf-8 -*-

import os

base_path = os.getcwd()

# Path to your req.txt file
req_file_path = 'req.txt'

# Read the req.txt file
with open(req_file_path, 'r') as f:
    packages = f.readlines()

# Extract package names
package_names = [pkg.split('==')[0].strip() for pkg in packages]

# Define hidden imports
hiddenimports = package_names

# Your existing code
a = Analysis(
    [os.path.join(base_path, 'yolo_method/main.py')],
    pathex=[os.path.join(base_path, 'yolo_method')],
    binaries=[],
    datas=[],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    cipher=None,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='collection'
)