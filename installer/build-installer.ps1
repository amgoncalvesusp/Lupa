<# Build the verified Windows executable and compile the Inno Setup installer. #>
param(
    [string]$PythonLauncher = "py",
    [string]$Iscc = ""
)

$ErrorActionPreference = "Stop"
$ProjectDir = Split-Path -Parent $PSScriptRoot
$BuildDir = Join-Path $ProjectDir "build-installer"
$DistDir = Join-Path $ProjectDir "dist-installer"
$VenvDir = Join-Path $ProjectDir ".build-venv"
$VenvPython = Join-Path $VenvDir "Scripts\python.exe"
$Payload = Join-Path $ProjectDir "dist\Lupa-installer.exe"

function Assert-ProjectChild([string]$Path) {
    $projectFull = [IO.Path]::GetFullPath($ProjectDir).TrimEnd('\') + '\'
    $targetFull = [IO.Path]::GetFullPath($Path)
    if (-not $targetFull.StartsWith($projectFull, [StringComparison]::OrdinalIgnoreCase)) {
        throw "Caminho fora do projeto: $targetFull"
    }
}

if (-not $Iscc) {
    $candidates = @(
        (Join-Path $env:LOCALAPPDATA "Programs\Inno Setup 6\ISCC.exe"),
        "C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        "C:\Program Files\Inno Setup 6\ISCC.exe"
    )
    $Iscc = $candidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
}

Assert-ProjectChild $BuildDir
Assert-ProjectChild $DistDir
Assert-ProjectChild $VenvDir

Push-Location $ProjectDir
try {
    if (Test-Path -LiteralPath $BuildDir) { Remove-Item -LiteralPath $BuildDir -Recurse -Force }
    if (Test-Path -LiteralPath $DistDir) { Remove-Item -LiteralPath $DistDir -Recurse -Force }
    if (Test-Path -LiteralPath $VenvDir) { Remove-Item -LiteralPath $VenvDir -Recurse -Force }

    & $PythonLauncher -3.11 -m venv $VenvDir
    if ($LASTEXITCODE -ne 0) { throw "Falha ao criar ambiente de build." }
    & $VenvPython -m pip install --disable-pip-version-check --upgrade pip
    & $VenvPython -m pip install --disable-pip-version-check -r requirements.txt pyinstaller
    if ($LASTEXITCODE -ne 0) { throw "Falha ao instalar dependencias do build." }
    & $VenvPython -c "from PyQt6.QtCore import PYQT_VERSION_STR, QT_VERSION_STR; assert PYQT_VERSION_STR == '6.6.1' and QT_VERSION_STR == '6.6.1', (PYQT_VERSION_STR, QT_VERSION_STR); print(f'Build Qt validado: PyQt {PYQT_VERSION_STR} / Qt {QT_VERSION_STR}')"
    if ($LASTEXITCODE -ne 0) { throw "Versoes PyQt/Qt incompativeis com o projeto." }

    & $VenvPython -m PyInstaller --noconfirm --clean --workpath $BuildDir --distpath $DistDir Lupa.spec
    if ($LASTEXITCODE -ne 0) { throw "PyInstaller falhou com código $LASTEXITCODE." }
    Copy-Item -LiteralPath (Join-Path $DistDir "Lupa.exe") -Destination $Payload -Force
    if (-not (Test-Path -LiteralPath $Iscc)) { throw "Inno Setup não encontrado: $Iscc" }
    & $Iscc (Join-Path $PSScriptRoot "Lupa.iss")
    if ($LASTEXITCODE -ne 0) { throw "Inno Setup falhou com código $LASTEXITCODE." }
} finally {
    Pop-Location
}


