<#
    Lupa — instalador local (sem dependencias externas).

    Copia dist\Lupa-installer.exe para %LOCALAPPDATA%\Programs\Lupa e cria atalhos no
    Menu Iniciar e na Area de Trabalho. Nao requer privilegios de administrador
    (instalacao por usuario).

    Uso:
        powershell -ExecutionPolicy Bypass -File installer\install.ps1
#>
$ErrorActionPreference = "Stop"

$AppName = "Lupa"
$ProjectDir = Split-Path -Parent $PSScriptRoot
$ExeSource = Join-Path $ProjectDir "dist\Lupa-installer.exe"

if (-not (Test-Path $ExeSource)) {
    Write-Error "Executavel nao encontrado: $ExeSource`nRode build.bat antes de instalar."
    exit 1
}

$InstallDir = Join-Path $env:LOCALAPPDATA "Programs\$AppName"
$ExeTarget = Join-Path $InstallDir "Lupa.exe"

Write-Host "Instalando $AppName em $InstallDir ..."
New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
Copy-Item -Path $ExeSource -Destination $ExeTarget -Force

# Copia o desinstalador para a pasta de instalacao
Copy-Item -Path (Join-Path $PSScriptRoot "uninstall.ps1") -Destination (Join-Path $InstallDir "uninstall.ps1") -Force -ErrorAction SilentlyContinue

$shell = New-Object -ComObject WScript.Shell

# Atalho no Menu Iniciar
$startMenuDir = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs"
$startLnk = Join-Path $startMenuDir "$AppName.lnk"
$sc = $shell.CreateShortcut($startLnk)
$sc.TargetPath = $ExeTarget
$sc.WorkingDirectory = $InstallDir
$sc.Description = "Lupa - Analise textual de documentos"
$sc.Save()

# Atalho na Area de Trabalho
$desktop = [Environment]::GetFolderPath("Desktop")
$desktopLnk = Join-Path $desktop "$AppName.lnk"
$dc = $shell.CreateShortcut($desktopLnk)
$dc.TargetPath = $ExeTarget
$dc.WorkingDirectory = $InstallDir
$dc.Description = "Lupa - Analise textual de documentos"
$dc.Save()

Write-Host "Instalacao concluida."
Write-Host "  Executavel: $ExeTarget"
Write-Host "  Atalhos:    Menu Iniciar e Area de Trabalho"
Write-Host "Para desinstalar: powershell -ExecutionPolicy Bypass -File `"$InstallDir\uninstall.ps1`""
