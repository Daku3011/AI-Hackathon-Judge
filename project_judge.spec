# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

import os

# Define paths
backend_path = os.path.join(os.getcwd(), 'backend')
frontend_dist_path = os.path.join(os.getcwd(), 'frontend', 'dist')

# Ensure frontend dist exists (Build script should handle this, but good check)
if not os.path.exists(frontend_dist_path):
    print(f"WARNING: '{frontend_dist_path}' does not exist. Frontend assets will be missing!")

a = Analysis(
    [os.path.join(backend_path, 'main.py')],
    pathex=[backend_path],
    binaries=[],
    datas=[
        (frontend_dist_path, 'frontend/dist'),
        (os.path.join(backend_path, 'VERSION'), '.'),
        (os.path.join(backend_path, 'services'), 'services'),
    ],
    hiddenimports=['uvicorn', 'fastapi', 'google.generativeai', 'youtube_transcript_api', 'pypdf', 'github', 'python_multipart', 'dotenv'],
    hookspath=[],
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
    exclude_binaries=True,
    name='project_judge',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='project_judge',
)
