# PyInstaller spec for CarpeSimiusSoundBoard
# Includes icon + branding assets in the packaged build.

from PyInstaller.utils.hooks import collect_submodules

block_cipher = None

hiddenimports = collect_submodules('webview')

# Bundle these files into the app folder (same directory as the EXE)
datas = [
    ('favicon.ico', '.'),
    ('logo.png', '.'),
    ('icon.png', '.'),
]


a = Analysis(
    ['soundboard.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='CarpeSimiusSoundBoard',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    icon='favicon.ico',
)
