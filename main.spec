# -*- mode: python ; coding: utf-8 -*-

import os

base_path = os.getcwd()

# Path to your req.txt file
req_file_path = os.path.join(base_path, 'req.txt')

# Read the req.txt file
with open(req_file_path, 'r') as f:
    packages = f.readlines()

# Extract package names
package_names = [pkg.split('==')[0].strip() for pkg in packages]

# Define hidden imports
hiddenimports = package_names

# Add external libraries explicitly if needed
hiddenimports.extend(['cv2', 'utils'])

media_path = os.path.join(base_path, 'media')
src_path = os.path.join(base_path, 'src')
yolo_method_path = os.path.join(src_path, 'yolo_method')
utils_path = os.path.join(src_path, 'utils')

# Check if the directories exist
if not os.path.exists(media_path):
    raise FileNotFoundError(f"Media directory not found: {media_path}")
if not os.path.exists(src_path):
    raise FileNotFoundError(f"Source directory not found: {src_path}")
if not os.path.exists(yolo_method_path):
    raise FileNotFoundError(f"YOLO method directory not found: {yolo_method_path}")
if not os.path.exists(utils_path):
    raise FileNotFoundError(f"Utils directory not found: {utils_path}")
if not os.path.exists(req_file_path):
    raise FileNotFoundError(f"req.txt file not found: {req_file_path}")

a = Analysis(
    [os.path.join(yolo_method_path, 'main.py')],
    pathex=[],
    binaries=[],
    datas=[
        (media_path, 'media'),  # Include media directory
        (src_path, 'src'),  # Include source directory
        (utils_path, 'utils'),  # Include utils directory
        (req_file_path, 'req.txt'),  # Include req.txt file
        # Add other necessary directories or files here
    ],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['.venv'],
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
    upx=False,
    upx_exclude=[],
    name='main.py',
    distpath=os.path.join(base_path, 'dist')
)