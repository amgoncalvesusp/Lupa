; Lupa — script Inno Setup para gerar um instalador (LupaSetup.exe).
;
; Pre-requisito: gerar dist\Lupa-installer.exe com Lupa.spec.
; Compilar: instalar o Inno Setup 6 e rodar
;     "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer\Lupa.iss
; Saida: installer\Output\LupaSetup.exe
;
; Enquanto o Inno Setup nao estiver instalado, use installer\install.ps1
; (instalador local sem dependencias).

#define AppName "Lupa"
#define AppVersion "1.0.1"
#define AppPublisher "UNIARA - Pesquisa Academica"
#define AppExeName "Lupa.exe"
#define AppSourceExe "..\dist\Lupa-installer.exe"

[Setup]
AppId={{B3F1A9C2-7E54-4D8A-9C1B-A0B1C2D3E4F5}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
DefaultDirName={localappdata}\Programs\{#AppName}
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
OutputDir=Output
OutputBaseFilename=LupaSetup-{#AppVersion}-x64
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
LicenseFile=..\LICENSE
SetupIconFile=..\src\gui\assets\lupa-icon.ico
UninstallDisplayIcon={app}\{#AppExeName}
VersionInfoVersion={#AppVersion}
VersionInfoCompany={#AppPublisher}
VersionInfoDescription=Instalador do Lupa
VersionInfoProductName={#AppName}
VersionInfoProductVersion={#AppVersion}
MinVersion=10.0.17763
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
CloseApplications=yes
RestartApplications=no

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Tasks]
Name: "desktopicon"; Description: "Criar atalho na Area de Trabalho"; GroupDescription: "Atalhos adicionais:"

[InstallDelete]
Type: files; Name: "{app}\uninstall.ps1"

[Files]
Source: "{#AppSourceExe}"; DestDir: "{app}"; DestName: "{#AppExeName}"; Flags: ignoreversion
Source: "..\README.md"; DestDir: "{app}"; Flags: ignoreversion isreadme

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExeName}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExeName}"; Description: "Iniciar o {#AppName}"; Flags: nowait postinstall skipifsilent
