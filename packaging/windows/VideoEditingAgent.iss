#ifndef StageRoot
  #define StageRoot "..\..\build\packaging\dist\VideoEditingAgent"
#endif
#ifndef OutputDir
  #define OutputDir "..\..\build\installer"
#endif
#ifndef AppVersion
  #define AppVersion "0.1.2"
#endif
#ifndef SourceSha
  #define SourceSha "development"
#endif

#define AppName "Video Editing Agent"
#define AppPublisher "Orange Lee"
#define AppExeName "VideoEditingAgent.exe"
#define AppId "{{9A3F2C7B-7C4D-4BA8-9E79-6D8C1C6B98A4}"

[Setup]
AppId={#AppId}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
VersionInfoVersion={#AppVersion}
VersionInfoDescription={#AppName} Windows Installer
DefaultDirName={localappdata}\Programs\Video Editing Agent
DefaultGroupName=Video Editing Agent
DisableProgramGroupPage=yes
DisableWelcomePage=no
OutputDir={#OutputDir}
OutputBaseFilename=VideoEditingAgent-Setup-{#AppVersion}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
CloseApplications=yes
RestartApplications=no
SetupLogging=yes
UsePreviousAppDir=yes
UsePreviousGroup=yes
UsePreviousTasks=yes
Uninstallable=yes
UninstallDisplayName={#AppName}
UninstallDisplayIcon={app}\{#AppExeName}
ChangesEnvironment=no
MinVersion=10.0

[Languages]
Name: "en"; MessagesFile: "compiler:Default.isl"
Name: "zhcn"; MessagesFile: "compiler:Languages\ChineseSimplified.isl"

[CustomMessages]
en.FullInstall=Planning + Automatic Editing
en.PlanningInstall=Planning only
en.CustomInstall=Custom installation
en.CoreComponent=Core App / Planning
en.EditingComponent=Media Analysis + Automatic Editing
en.DesktopIcon=Create a desktop shortcut
zhcn.FullInstall=拍摄规划 + 自动剪辑
zhcn.PlanningInstall=仅拍摄规划
zhcn.CustomInstall=自定义安装
zhcn.CoreComponent=核心程序 / 拍摄规划
zhcn.EditingComponent=媒体分析 + 自动剪辑
zhcn.DesktopIcon=创建桌面快捷方式

[Types]
Name: "full"; Description: "{cm:FullInstall}"
Name: "planning"; Description: "{cm:PlanningInstall}"
Name: "custom"; Description: "{cm:CustomInstall}"; Flags: iscustom

[Components]
Name: "core"; Description: "{cm:CoreComponent}"; Types: full planning custom; Flags: fixed
Name: "editing"; Description: "{cm:EditingComponent}"; Types: full

[Tasks]
Name: "desktopicon"; Description: "{cm:DesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Core contains the application/private Python/Tk/resources, but not Editing runtimes
; or deferred 2.0 speech payloads. Excludes are defense-in-depth if an engineering
; staging tree still contains historical speech proof artifacts.
Source: "{#StageRoot}\*"; DestDir: "{app}"; Components: core; Flags: ignoreversion recursesubdirs; Excludes: "_internal\tools\*,_internal\runtimes\transnet\*,_internal\runtimes\speech\*,_internal\models\faster-whisper-base\*"

; Editing capability is optional so Planning-only users do not acquire heavy media
; runtimes merely because the product supports automatic editing.
Source: "{#StageRoot}\_internal\tools\*"; DestDir: "{app}\_internal\tools"; Components: editing; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "{#StageRoot}\_internal\runtimes\transnet\*"; DestDir: "{app}\_internal\runtimes\transnet"; Components: editing; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Video Editing Agent"; Filename: "{app}\{#AppExeName}"
Name: "{autodesktop}\Video Editing Agent"; Filename: "{app}\{#AppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(AppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
