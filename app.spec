# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files

# 收集 Lupa 的数据文件
lupa_datas = collect_data_files('lupa')

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
        datas=[
        ('templates/*', 'templates'),
        ('static/assets/*', 'static/assets'),
        ('static/vite.svg', 'static'),
        ('cluster/template/Caves/*', 'cluster/template/Caves'),
        ('cluster/template/Master/*', 'cluster/template/Master'),
        ('cluster/template/*', 'cluster/template'),
    ] + lupa_datas,  # 添加 Lupa 的数据文件
    hiddenimports=['engineio.async_drivers.threading','lupa'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='app',
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
    name='app',
)
