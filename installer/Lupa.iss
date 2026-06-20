; Lupa — script Inno Setup para gerar um instalador (LupaSetup.exe).
;
; Pre-requisito: rodar build.bat antes (gera dist\Lupa.exe).
; Compilar: instalar o Inno Setup 6 e rodar
;     "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer\Lupa.iss
; Saida: installer\Output\LupaSetup.exe
;
; Enquanto o Inno Setup nao estiver instalado, use installer\install.ps1
; (instalador local sem dependencias).

#define AppName "Lupa"
#define AppVersion "1.0.0"
#define AppPublisher "UNIARA - Pesquisa Academica"
#define AppExeName "Lupa.exe"

[Setup]
AppId={{B3F1A9C2-7E54-4D8A-9C1B-A0B1C2D3E4F5}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
OutputDir=Output
OutputBaseFilename=LupaSetup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequiredOverridesAllowed=dialog
LicenseFile=..\LICENSE
SetupIconFile=..\src\gui\assets\lupa-icon.ico
UninstallDisplayIcon={app}\{#AppExeName}
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Tasks]
Name: "desktopicon"; Description: "Criar atalho na Area de Trabalho"; GroupDescription: "Atalhos adicionais:"

[Files]
Source: "..\dist\Lupa.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\README.md"; DestDir: "{app}"; Flags: ignoreversion isreadme

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExeName}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExeName}"; Description: "Iniciar o {#AppName}"; Flags: nowait postinstall skipifsilent
