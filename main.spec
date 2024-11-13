# -*- mode: python ; coding: utf-8 -*-

import os
import tempfile
from PyInstaller.utils.hooks import collect_data_files
from ultralytics import YOLO

# Defina o diretório temporário para o modelo
model_dir = os.path.join(tempfile.gettempdir(), 'yolo_models')
os.makedirs(model_dir, exist_ok=True)  # Garante que o diretório existe

# Colete arquivos necessários da biblioteca ultralytics
ultra_files = collect_data_files('ultralytics')

base_path = os.getcwd()

# Caminho para o arquivo req.txt
req_file_path = os.path.join(base_path, 'req.txt')

# Leia o arquivo req.txt
with open(req_file_path, 'r') as f:
    packages = f.readlines()

# Extraia os nomes dos pacotes
package_names = [pkg.split('==')[0].strip() for pkg in packages]

# Defina as importações ocultas
hiddenimports = package_names
hiddenimports.extend(['cv2', 'utils'])  # Adicione bibliotecas externas explicitamente, se necessário

# Defina os caminhos para as outras pastas e verifique sua existência
media_path = os.path.join(base_path, 'media')
src_path = os.path.join(base_path, 'src')
yolo_method_path = os.path.join(src_path, 'yolo_method')
utils_path = os.path.join(src_path, 'utils')

for path, name in [(media_path, "Media"), (src_path, "Source"), 
                   (yolo_method_path, "YOLO method"), (utils_path, "Utils"), 
                   (req_file_path, "req.txt")]:
    if not os.path.exists(path):
        raise FileNotFoundError(f"{name} directory not found: {path}")

a = Analysis(
    [os.path.join(yolo_method_path, 'PeopleCounter.py')],
    pathex=[],
    binaries=[],
    datas=[
        (media_path, 'media'),  # Inclui o diretório media
        (src_path, 'src'),  # Inclui o diretório src
        (utils_path, 'utils'),  # Inclui o diretório utils
        (req_file_path, 'req.txt'),  # Inclui o arquivo req.txt
        (model_dir, 'yolo_models'),  # Inclui o diretório do modelo no executável
        *ultra_files,  # Expande ultra_files como uma lista de tuplas
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
    name='PeopleCounter.py',
    distpath=os.path.join(base_path, 'dist')
)
