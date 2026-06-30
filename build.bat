@echo off
REM Build the standalone Windows executable using the reviewed PyInstaller spec.

setlocal
cd /d "%~dp0"

echo === Installing build dependencies ===
py -3.11 -m pip install -r requirements.txt
py -3.11 -m pip install pyinstaller
if errorlevel 1 exit /b 1

echo.
echo === Building Lupa.exe ===
py -3.11 -m PyInstaller --noconfirm --clean Lupa.spec
if errorlevel 1 (
    echo === Build failed ===
    exit /b 1
)

echo.
echo === Build complete: dist\Lupa.exe ===
endlocal
