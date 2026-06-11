@echo off
REM Build standalone executable "Lupa" for Windows with PyInstaller.

setlocal

set PROJECT_DIR=%~dp0
cd /d "%PROJECT_DIR%"

echo === Installing dependencies ===
pip install -r requirements.txt
pip install pyinstaller

echo.
echo === Building executable ===

set "TESS_DIR=C:\Program Files\Tesseract-OCR"

REM Only the PyQt6 modules actually used: QtCore, QtGui, QtWidgets.
REM Exclude heavy Qt modules we don't use to reduce build time and exe size.
set PYQT_EXCLUDES=^
    --exclude-module PyQt6.QtBluetooth ^
    --exclude-module PyQt6.QtCharts ^
    --exclude-module PyQt6.QtDBus ^
    --exclude-module PyQt6.QtDataVisualization ^
    --exclude-module PyQt6.QtDesigner ^
    --exclude-module PyQt6.QtHelp ^
    --exclude-module PyQt6.QtMultimedia ^
    --exclude-module PyQt6.QtMultimediaWidgets ^
    --exclude-module PyQt6.QtNetwork ^
    --exclude-module PyQt6.QtNfc ^
    --exclude-module PyQt6.QtOpenGL ^
    --exclude-module PyQt6.QtOpenGLWidgets ^
    --exclude-module PyQt6.QtPdf ^
    --exclude-module PyQt6.QtPdfWidgets ^
    --exclude-module PyQt6.QtPositioning ^
    --exclude-module PyQt6.QtPrintSupport ^
    --exclude-module PyQt6.QtQml ^
    --exclude-module PyQt6.QtQuick ^
    --exclude-module PyQt6.QtQuick3D ^
    --exclude-module PyQt6.QtQuickWidgets ^
    --exclude-module PyQt6.QtRemoteObjects ^
    --exclude-module PyQt6.QtSensors ^
    --exclude-module PyQt6.QtSerialPort ^
    --exclude-module PyQt6.QtSpatialAudio ^
    --exclude-module PyQt6.QtSql ^
    --exclude-module PyQt6.QtSvg ^
    --exclude-module PyQt6.QtSvgWidgets ^
    --exclude-module PyQt6.QtTest ^
    --exclude-module PyQt6.QtTextToSpeech ^
    --exclude-module PyQt6.QtWebChannel ^
    --exclude-module PyQt6.QtWebEngineCore ^
    --exclude-module PyQt6.QtWebEngineWidgets ^
    --exclude-module PyQt6.QtWebSockets ^
    --exclude-module PyQt6.QtXml

if exist "%TESS_DIR%\tesseract.exe" (
    echo Tesseract detected: bundling into executable
    pyinstaller --noconfirm ^
        --onefile ^
        --windowed ^
        --name "Lupa" ^
        --add-data "%TESS_DIR%;tesseract" ^
        --hidden-import PyQt6.QtCore ^
        --hidden-import PyQt6.QtGui ^
        --hidden-import PyQt6.QtWidgets ^
        --collect-submodules fitz ^
        --collect-submodules openpyxl ^
        --collect-submodules regex ^
        --collect-submodules pytesseract ^
        --hidden-import src.core.analysis.vendor.leia.leia ^
        --collect-data src.core.analysis.vendor.leia ^
        --add-data "src\core\data;src\core\data" ^
        %PYQT_EXCLUDES% ^
        src\main.py
) else (
    echo WARNING: Tesseract not found at %TESS_DIR%
    echo OCR feature will require user-side Tesseract install.
    pyinstaller --noconfirm ^
        --onefile ^
        --windowed ^
        --name "Lupa" ^
        --hidden-import PyQt6.QtCore ^
        --hidden-import PyQt6.QtGui ^
        --hidden-import PyQt6.QtWidgets ^
        --collect-submodules fitz ^
        --collect-submodules openpyxl ^
        --collect-submodules regex ^
        --collect-submodules pytesseract ^
        --hidden-import src.core.analysis.vendor.leia.leia ^
        --collect-data src.core.analysis.vendor.leia ^
        --add-data "src\core\data;src\core\data" ^
        %PYQT_EXCLUDES% ^
        src\main.py
)

if %ERRORLEVEL% EQU 0 (
    echo.
    echo === Build complete ===
    echo Executable: dist\Lupa.exe
) else (
    echo.
    echo === Build failed ===
    exit /b 1
)

endlocal
