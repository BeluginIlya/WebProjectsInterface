# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['Start.py'],
    pathex=[],
    binaries=[('C:\\Users\\belug\\Documents\\PythonProjects\\WebInterfaceForProjects\\venv\\Lib\\site-packages\\snap7\\lib\\snap7.dll', '.')],
    datas=[('db.sqlite3', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Start',
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
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Start',
)
