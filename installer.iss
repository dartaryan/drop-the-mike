; ============================================================
; Inno Setup Script - DROP THE MIKE Windows Installer
; Requires Inno Setup 6.x+ (https://jrsoftware.org/isinfo.php)
;
; Build: iscc installer.iss
; Or with version override: iscc /DMyAppVersion=1.2.0 installer.iss
; ============================================================

#ifndef MyAppVersion
  #define MyAppVersion "1.0.0"
#endif

#define MyAppName      "DROP THE MIKE"
#define MyAppPublisher "Ben Akiva"
#define MyAppURL       "https://dartaryan.github.io/drop-the-mike/"
#define MyAppExeName   "DropTheMike.exe"

; PyInstaller output folder (set via /DSourceDir=... or default)
#ifndef SourceDir
  #define SourceDir "dist\DropTheMike"
#endif

[Setup]
AppId={{E7A3B5C1-4D2F-4A89-9B1E-3C5D7F8A2B04}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
DefaultDirName={autopf}\DropTheMike
DefaultGroupName={#MyAppName}
OutputDir=.\Output
OutputBaseFilename=DropTheMike-Setup
SetupIconFile=icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0
PrivilegesRequired=admin
DisableProgramGroupPage=yes
; No license page — open source, keep install simple
DisableWelcomePage=no

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
; Hebrew not available in Inno by default; English is fine for the installer

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; \
    GroupDescription: "{cm:AdditionalIcons}"

[Files]
; Main application (PyInstaller --onedir output)
Source: "{#SourceDir}\{#MyAppExeName}"; DestDir: "{app}"; \
    Flags: ignoreversion
Source: "{#SourceDir}\*"; DestDir: "{app}"; \
    Flags: ignoreversion recursesubdirs createallsubdirs; \
    Excludes: "ffmpeg\*"

; FFmpeg binaries (placed by CI into the dist folder)
Source: "{#SourceDir}\ffmpeg\ffmpeg.exe"; DestDir: "{app}\ffmpeg"; \
    Flags: ignoreversion
Source: "{#SourceDir}\ffmpeg\ffprobe.exe"; DestDir: "{app}\ffmpeg"; \
    Flags: ignoreversion

[Icons]
; Start Menu shortcut
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; \
    WorkingDir: "{app}"; Comment: "Split audio & video for transcription"
; Start Menu uninstall shortcut
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"
; Desktop shortcut (optional, user-selectable — checked by default)
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; \
    Tasks: desktopicon; WorkingDir: "{app}"

[Run]
; Launch app after install
Filename: "{app}\{#MyAppExeName}"; \
    Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; \
    Flags: nowait postinstall skipifsilent
