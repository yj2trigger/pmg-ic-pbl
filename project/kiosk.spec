# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['src/app/main.py'],
    pathex=['src'],
    binaries=[],
    datas=[
        # 초기 데이터 파일을 exe에 번들 → 첫 실행 시 AppData로 복사
        ('src/app/data/products.json',    'data'),
        ('src/app/data/ingredients.json', 'data'),
        ('src/app/data/options.json',     'data'),
    ],
    hiddenimports=[
        'PyQt6',
        'PyQt6.QtWidgets',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'edge_tts',
        'pygame',
        'pygame.mixer',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# --onefile: 모든 의존성을 단일 exe로 묶음
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='kiosk',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,   # GUI 앱: 콘솔 창 없음
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
