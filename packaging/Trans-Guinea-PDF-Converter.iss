#define MyAppName "Trans-Guinea PDF Converter"
#define MyAppPublisher "IMakKushwaha"
#ifndef MyAppVersion
  #define MyAppVersion "0.1.2"
#endif
#define MyAppExeName "Trans-Guinea PDF Converter.exe"

[Setup]
AppId={{C0E6E9C7-0B8D-4EB4-9D1D-6B2AF5A1A0F1}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\Trans-Guinea PDF Converter
DefaultGroupName={#MyAppName}
OutputDir=..\release
OutputBaseFilename=Trans-Guinea-PDF-Converter-Setup-{#MyAppVersion}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayName={#MyAppName}
UninstallDisplayIcon={app}\{#MyAppExeName}
SetupIconFile=..\assets\app.ico
LicenseFile=..\LICENSE
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional shortcuts:"

[Files]
Source: "..\dist\Trans-Guinea PDF Converter\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\NOTICE"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\AUTHORS.md"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: postinstall nowait skipifsilent