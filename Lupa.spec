# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules

hiddenimports = ['PyQt6.QtCore', 'PyQt6.QtGui', 'PyQt6.QtWidgets']
hiddenimports += collect_submodules('fitz')
hiddenimports += collect_submodules('openpyxl')
hiddenimports += collect_submodules('regex')
hiddenimports += collect_submodules('pytesseract')
# Vendored LeIA (VADER-PT) sentiment engine — imported lazily.
hiddenimports += ['src.core.analysis.vendor.leia.leia']


a = Analysis(
    ['C:\\Users\\adria\\OneDrive\\Documents\\Projetos IA\\Lupa\\src\\main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('C:\\Program Files\\Tesseract-OCR', 'tesseract'),
        ('src/core/analysis/vendor/leia/lexicons', 'src/core/analysis/vendor/leia/lexicons'),
        ('src/core/data', 'src/core/data'),
    ],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['PyQt6.QtBluetooth', 'PyQt6.QtCharts', 'PyQt6.QtDBus', 'PyQt6.QtDesigner', 'PyQt6.QtHelp', 'PyQt6.QtMultimedia', 'PyQt6.QtMultimediaWidgets', 'PyQt6.QtNetwork', 'PyQt6.QtOpenGL', 'PyQt6.QtOpenGLWidgets', 'PyQt6.QtPdf', 'PyQt6.QtPdfWidgets', 'PyQt6.QtPositioning', 'PyQt6.QtPrintSupport', 'PyQt6.QtQml', 'PyQt6.QtQuick', 'PyQt6.QtQuick3D', 'PyQt6.QtQuickWidgets', 'PyQt6.QtRemoteObjects', 'PyQt6.QtSensors', 'PyQt6.QtSerialPort', 'PyQt6.QtSpatialAudio', 'PyQt6.QtSql', 'PyQt6.QtSvg', 'PyQt6.QtSvgWidgets', 'PyQt6.QtTest', 'PyQt6.QtTextToSpeech', 'PyQt6.QtWebChannel', 'PyQt6.QtWebEngineCore', 'PyQt6.QtWebEngineWidgets', 'PyQt6.QtWebSockets', 'PyQt6.QtXml'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Lupa',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
