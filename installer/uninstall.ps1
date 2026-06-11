<#
    Lupa — desinstalador local.

    Remove a pasta de instalacao e os atalhos do Menu Iniciar e da Area de
    Trabalho. Nao toca em planilhas exportadas pelo usuario.

    Uso:
        powershell -ExecutionPolicy Bypass -File uninstall.ps1
#>
$ErrorActionPreference = "SilentlyContinue"

$AppName = "Lupa"
$InstallDir = Join-Path $env:LOCALAPPDATA "Programs\$AppName"
$startLnk = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs\$AppName.lnk"
$desktopLnk = Join-Path ([Environment]::GetFolderPath("Desktop")) "$AppName.lnk"

Write-Host "Desinstalando $AppName ..."
Remove-Item -Path $startLnk -Force
Remove-Item -Path $desktopLnk -Force
Remove-Item -Path $InstallDir -Recurse -Force

Write-Host "Desinstalacao concluida."
