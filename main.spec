# -*- mode: python ; coding: utf-8 -*-
import os
import subprocess
import importlib.util

# Ensure the yolo_models directory exists
def ensure_model_dir_exists():
    model_dir = os.path.join(os.getcwd(), 'yolo_models')
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)
        print(f"Created directory: {model_dir}")
    else:
        print(f"Directory already exists: {model_dir}")

# Check if YOLO is installed
def ensure_yolo_installed():
    package_name = "ultralytics"  # YOLO package name
    if importlib.util.find_spec(package_name) is None:
        print(f"{package_name} not found. Installing...")
        subprocess.run(["pip", "install", package_name], check=True)
    else:
        print(f"{package_name} is already installed.")

# Ensure the yolo_models directory exists
ensure_model_dir_exists()

# Ensure YOLO is installed
ensure_yolo_installed()

# Your existing .spec code continues below
from PyInstaller.utils.hooks import collect_data_files
from ultralytics import YOLO

base_path = os.getcwd()
media_path = os.path.join(base_path, 'media')
src_path = os.path.join(base_path, 'src')
yolo_method_path = os.path.join(src_path, 'yolo_method')
utils_path = os.path.join(src_path, 'utils')
req_file_path = os.path.join(base_path, 'req.txt')
model_dir = os.path.join(base_path, 'yolo_models')

ultra_files = collect_data_files('ultralytics')

# Define Analysis
a = Analysis(
    [os.path.join(yolo_method_path, 'PeopleCounter.py')],
    pathex=[],
    binaries=[],
    datas=[
        (media_path, 'media'),
        (src_path, 'src'),
        (utils_path, 'utils'),
        (req_file_path, 'req.txt'),
        (model_dir, 'yolo_models'),
        *ultra_files,
    ],
    hiddenimports=[],
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
    name='main',  # Update this to match the EXE name
    distpath=os.path.join(base_path, 'dist'),
)
