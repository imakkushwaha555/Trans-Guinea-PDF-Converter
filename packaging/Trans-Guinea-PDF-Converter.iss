#define MyAppName "Trans-Guinea PDF Converter"
#define MyAppPublisher "Trans-Guinea PDF Converter contributors"
#define MyAppVersion "0.1.0"
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
ArchitecturesInstallIn64BitMode=x64
UninstallDisplayName={#MyAppName}
PrivilegesRequired=admin

[Files]
Source: "..\dist\Trans-Guinea PDF Converter\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: postinstall nowait skipifsilent