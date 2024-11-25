# -*- mode: python ; coding: utf-8 -*-
import os
import subprocess
import importlib.util

# Ensure the yolo_models directory exists
def ensure_model_dir_exists():
    model_dir = os.path.join(os.getcwd(), 'yolo_models')
    print(f"Checking if model directory exists at: {model_dir}")
    if not os.path.exists(model_dir):
        try:
            os.makedirs(model_dir, exist_ok=True)
            print(f"Created directory: {model_dir}")
        except PermissionError:
            print(f"Permission denied: {model_dir}. Trying to set permissions...")
            os.chmod(model_dir, 0o755)
            os.makedirs(model_dir, exist_ok=True)
            print(f"Created directory with updated permissions: {model_dir}")
    else:
        print(f"Directory already exists: {model_dir}")

# Check if YOLO is installed
def ensure_yolo_installed():
    package_name = "ultralytics"  # YOLO package name
    print(f"Checking if package '{package_name}' is installed...")
    if importlib.util.find_spec(package_name) is None:
        print(f"{package_name} not found. Installing...")
        subprocess.run(["pip", "install", package_name], check=True)
        print(f"Successfully installed {package_name}")
    else:
        print(f"{package_name} is already installed.")

# Ensure the yolo_models directory exists
print("Ensuring YOLO models directory exists...")
ensure_model_dir_exists()

# Ensure YOLO is installed
print("Ensuring YOLO is installed...")
ensure_yolo_installed()

# Your existing .spec code continues below
from PyInstaller.utils.hooks import collect_data_files
from ultralytics import YOLO

print("Collecting data files for ultralytics...")
ultra_files = collect_data_files('ultralytics')
print(f"Collected {len(ultra_files)} data files for ultralytics.")

base_path = os.getcwd()
media_path = os.path.join(base_path, 'media')
src_path = os.path.join(base_path, 'src')
yolo_method_path = os.path.join(src_path, 'yolo_method')
utils_path = os.path.join(src_path, 'utils')
req_file_path = os.path.join(base_path, 'req.txt')
model_dir = os.path.join(base_path, 'yolo_models')

# Read requirements from req.txt for hiddenimports
hidden_imports_list = []
if os.path.exists(req_file_path):
    with open(req_file_path, 'r') as req_file:
        hidden_imports_list = [line.strip() for line in req_file if line.strip() and not line.startswith('#')]
    print(f"Hidden imports from req.txt: {hidden_imports_list}")
else:
    print(f"Error: req.txt file not found at {req_file_path}")

# Define Analysis
print("Defining PyInstaller Analysis...")
a = Analysis(
    [os.path.join(yolo_method_path, 'PeopleCounter.py')],
    pathex=[yolo_method_path],
    binaries=[],
    datas=[
        (media_path, 'media'),
        (src_path, 'src'),
        (utils_path, 'utils'),
        (req_file_path, 'req.txt'),
        (model_dir, 'yolo_models'),
        *ultra_files,
    ],
    hiddenimports=['ultralytics', *hidden_imports_list],  # Explicitly include YOLO package and libraries from req.txt
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['.venv'],
    noarchive=False,
    cipher=None,
)
print("Analysis defined successfully.")

print("Creating PYZ...")
pyz = PYZ(a.pure, a.zipped_data, cipher=None)
print("PYZ created successfully.")

print("Creating EXE...")
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='myapp',  # Update this to match the desired EXE name
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
)
print("EXE created successfully.")

print("Creating COLLECT...")
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='myapp_dist',  # Update this to match the desired folder name
    distpath=os.path.join(base_path, 'dist'),  # Ensure this is a valid directory
)
print("COLLECT created successfully.")
