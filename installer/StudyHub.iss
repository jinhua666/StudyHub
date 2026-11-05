#define AppName "StudyHub"
#define AppVersion "1.0.2"

[Setup]
AppId={{95A4A615-37C2-4777-A3E3-7765E0C3E784}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher=StudyHub
DefaultDirName={localappdata}\Programs\StudyHub
DisableDirPage=no
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
OutputDir=..\installer-output
OutputBaseFilename=StudyHub-Setup
SetupIconFile=..\assets\studyhub.ico
UninstallDisplayIcon={app}\StudyHub.exe
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
CloseApplications=yes
UninstallDisplayName=StudyHub

[Languages]
Name: "chinesesimp"; MessagesFile: "compiler:Default.isl,ChineseSimplified.isl"

[Tasks]
Name: "desktopicon"; Description: "创建桌面快捷方式"; GroupDescription: "快捷方式："

[Files]
Source: "..\release\StudyHub\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\studyhub-learning-doc\SKILL.md"; DestDir: "{app}\skill\studyhub-learning-doc"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\StudyHub"; Filename: "{app}\StudyHub.exe"
Name: "{autodesktop}\StudyHub"; Filename: "{app}\StudyHub.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\StudyHub.exe"; Description: "启动 StudyHub"; Flags: nowait postinstall skipifsilent

[Code]
procedure CurStepChanged(CurStep: TSetupStep);
var
  CodexHome, SkillDir, SourceFile, TargetFile, BackupFile: String;
  Index: Integer;
begin
  if CurStep <> ssPostInstall then exit;
  CodexHome := GetEnv('CODEX_HOME');
  if CodexHome = '' then begin
    CodexHome := GetEnv('USERPROFILE');
    if CodexHome = '' then
      RaiseException('无法获取当前用户目录，无法自动安装技能。');
    CodexHome := AddBackslash(CodexHome) + '.codex';
  end;
  if ExtractFileDrive(CodexHome) = '' then
    RaiseException('CODEX_HOME 必须是绝对路径，无法自动安装技能。');
  SkillDir := AddBackslash(CodexHome) + 'skills\studyhub-learning-doc';
  if not ForceDirectories(SkillDir) then
    RaiseException('无法创建 Codex 技能目录：' + SkillDir);
  SourceFile := ExpandConstant('{app}\skill\studyhub-learning-doc\SKILL.md');
  TargetFile := AddBackslash(SkillDir) + 'SKILL.md';
  if FileExists(TargetFile) and (GetSHA256OfFile(SourceFile) <> GetSHA256OfFile(TargetFile)) then begin
    BackupFile := TargetFile + '.before-studyhub-install-' + GetDateTimeString('yyyymmdd-hhnnss', '-', ':');
    Index := 0;
    while FileExists(BackupFile) do begin
      Index := Index + 1;
      BackupFile := TargetFile + '.before-studyhub-install-' + GetDateTimeString('yyyymmdd-hhnnss', '-', ':') + '-' + IntToStr(Index);
    end;
    if not FileCopy(TargetFile, BackupFile, True) then
      RaiseException('无法备份已有的学习文档技能，安装已停止。');
  end;
  if not FileCopy(SourceFile, TargetFile, False) then
    RaiseException('无法自动安装学习文档技能：' + TargetFile);
end;
