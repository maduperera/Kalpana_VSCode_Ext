# -*- mode: python ; coding: utf-8 -*-


import glob

so_files = glob.glob('core*.so') + glob.glob('core*.pyd')
binaries_list = [(f, '.') for f in so_files]

a = Analysis(
    ['api_server.py'],
    pathex=['.'],
    binaries=binaries_list,
    datas=[],
    hiddenimports=['torch', 'fastapi', 'pydantic', 'httpx'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['core', 'matplotlib', 'PIL', 'sympy', 'boto', 'locket', 'sklearn', 'scipy', 'PyQt5', 'tkinter', 'nltk', 'pandas', 'cv2', 'gevent', 'zope', 'keyring', 'bokeh', 'transformers', 'datasets', 'tensorflow'],
    noarchive=False,
    optimize=2,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='kalpana-engine-mac',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
