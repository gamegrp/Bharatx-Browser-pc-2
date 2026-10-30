; BharatX Browser - Windows setup (.exe) built with Inno Setup 6.
; Build: ISCC.exe /DAppVersion=1.36.0 /DPayloadDir=<payload> /DOutputDir=<out> /DRepoRoot=<repo> installer.iss
#ifndef AppVersion
  #define AppVersion "1.36.0"
#endif
#ifndef PayloadDir
  #define PayloadDir "..\..\payload"
#endif
#ifndef OutputDir
  #define OutputDir "..\..\out"
#endif
#ifndef RepoRoot
  #define RepoRoot "..\.."
#endif

[Setup]
AppId={{6B1F5C0E-4B7A-4D52-9E0B-3A7C1D2E8F41}
AppName=BharatX Browser
AppVersion={#AppVersion}
AppPublisher=Nitai Studio
AppPublisherURL=https://www.trishabonlineservice.in/
AppSupportURL=https://www.trishabonlineservice.in/
DefaultDirName={autopf}\BharatX Browser
DefaultGroupName=BharatX Browser
DisableProgramGroupPage=yes
UninstallDisplayIcon={app}\BharatXBrowser.exe
SetupIconFile={#RepoRoot}\branding\BharatXBrowser.ico
OutputDir={#OutputDir}
OutputBaseFilename=BharatXBrowser-Setup-{#AppVersion}-x64
Compression=lzma2/max
SolidCompression=yes
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
WizardStyle=modern
CloseApplications=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "{#PayloadDir}\*"; DestDir: "{app}"; Excludes: "AppxManifest.xml"; Flags: recursesubdirs createallsubdirs ignoreversion
Source: "{#RepoRoot}\LICENSE"; DestDir: "{app}"; DestName: "LICENSE.txt"; Flags: ignoreversion

[Icons]
Name: "{group}\BharatX Browser"; Filename: "{app}\BharatXBrowser.exe"
Name: "{autodesktop}\BharatX Browser"; Filename: "{app}\BharatXBrowser.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\BharatXBrowser.exe"; Description: "{cm:LaunchProgram,BharatX Browser}"; Flags: nowait postinstall skipifsilent
