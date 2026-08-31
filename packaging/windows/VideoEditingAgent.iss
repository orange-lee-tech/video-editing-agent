#ifndef StageRoot
  #define StageRoot "..\..\build\packaging\dist\VideoEditingAgent"
#endif
#ifndef OutputDir
  #define OutputDir "..\..\build\installer"
#endif
#ifndef AppVersion
  #define AppVersion "1.0.0"
#endif
#ifndef SourceSha
  #define SourceSha "development"
#endif

#define AppName "有岐"
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
DefaultGroupName=有岐
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
Name: "en"; MessagesFile: "compiler:Default.isl"; LicenseFile: "..\..\resources\legal\USER_AGREEMENT_en.txt"
Name: "zhcn"; MessagesFile: "compiler:Languages\ChineseSimplified.isl"; LicenseFile: "..\..\resources\legal\USER_AGREEMENT_zh-CN.txt"

[CustomMessages]
en.FullInstall=Planning + Automatic Editing
en.PlanningInstall=Planning only
en.CustomInstall=Custom installation
en.CoreComponent=Core App / Planning
en.EditingComponent=Media Analysis + Automatic Editing
en.DesktopIcon=Create a desktop shortcut
en.InstallEtaEstimating=Estimating remaining installation time...
en.InstallEtaRemaining=Estimated remaining: %1
en.InstallEtaMinuteSecond=%1 min %2 sec
en.InstallEtaSecond=%1 sec
zhcn.FullInstall=拍摄规划 + 自动剪辑
zhcn.PlanningInstall=仅拍摄规划
zhcn.CustomInstall=自定义安装
zhcn.CoreComponent=核心程序 / 拍摄规划
zhcn.EditingComponent=媒体分析 + 自动剪辑
zhcn.DesktopIcon=创建桌面快捷方式
zhcn.InstallEtaEstimating=正在估算剩余安装时间...
zhcn.InstallEtaRemaining=预计剩余：%1
zhcn.InstallEtaMinuteSecond=%1 分 %2 秒
zhcn.InstallEtaSecond=%1 秒

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
Source: "..\..\resources\legal\USER_AGREEMENT_en.txt"; DestDir: "{app}\licenses"; Components: core; Flags: ignoreversion
Source: "..\..\resources\legal\USER_AGREEMENT_zh-CN.txt"; DestDir: "{app}\licenses"; Components: core; Flags: ignoreversion

[Icons]
Name: "{group}\有岐"; Filename: "{app}\{#AppExeName}"
Name: "{autodesktop}\有岐"; Filename: "{app}\{#AppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(AppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent


[Code]
var
  InstallEtaLabel: TNewStaticText;
  InstallStartedTick: LongWord;
  SmoothedRemainingSeconds: Integer;

function GetTickCount: LongWord;
external 'GetTickCount@kernel32.dll stdcall';

function FormatInstallRemaining(Seconds: Integer): String;
var
  Minutes: Integer;
  Remainder: Integer;
begin
  if Seconds < 1 then
    Seconds := 1;
  Minutes := Seconds div 60;
  Remainder := Seconds mod 60;
  if Minutes > 0 then
    Result := FmtMessage(CustomMessage('InstallEtaMinuteSecond'), [
      IntToStr(Minutes), IntToStr(Remainder)])
  else
    Result := FmtMessage(CustomMessage('InstallEtaSecond'), [IntToStr(Remainder)]);
end;

procedure InitializeWizard;
begin
  InstallEtaLabel := TNewStaticText.Create(WizardForm);
  InstallEtaLabel.Parent := WizardForm.InstallingPage;
  InstallEtaLabel.Left := WizardForm.ProgressGauge.Left;
  InstallEtaLabel.Top :=
    WizardForm.ProgressGauge.Top + WizardForm.ProgressGauge.Height + ScaleY(8);
  InstallEtaLabel.Width := WizardForm.ProgressGauge.Width;
  InstallEtaLabel.Height := ScaleY(20);
  InstallEtaLabel.AutoSize := False;
  InstallEtaLabel.Font.Color := WizardForm.FilenameLabel.Font.Color;
  InstallEtaLabel.Caption := CustomMessage('InstallEtaEstimating');
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssInstall then
  begin
    InstallStartedTick := GetTickCount;
    SmoothedRemainingSeconds := 0;
    InstallEtaLabel.Caption := CustomMessage('InstallEtaEstimating');
  end;
end;

procedure CurInstallProgressChanged(CurProgress, MaxProgress: Integer);
var
  ElapsedSeconds: Integer;
  RawRemainingSeconds: Integer;
  ProgressPercent: Integer;
begin
  if (CurProgress <= 0) or (MaxProgress <= 0) or (InstallStartedTick = 0) then
  begin
    InstallEtaLabel.Caption := CustomMessage('InstallEtaEstimating');
    Exit;
  end;

  ElapsedSeconds := Integer((GetTickCount - InstallStartedTick) div 1000);
  ProgressPercent := (CurProgress * 100) div MaxProgress;
  if (ElapsedSeconds < 2) or (ProgressPercent < 3) then
  begin
    InstallEtaLabel.Caption := CustomMessage('InstallEtaEstimating');
    Exit;
  end;

  RawRemainingSeconds :=
    (ElapsedSeconds * (MaxProgress - CurProgress)) div CurProgress;
  if SmoothedRemainingSeconds <= 0 then
    SmoothedRemainingSeconds := RawRemainingSeconds
  else
    SmoothedRemainingSeconds :=
      ((SmoothedRemainingSeconds * 2) + RawRemainingSeconds) div 3;

  InstallEtaLabel.Caption := FmtMessage(CustomMessage('InstallEtaRemaining'), [
    FormatInstallRemaining(SmoothedRemainingSeconds)]);
end;
