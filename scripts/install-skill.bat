@echo off
setlocal
set "SKILL_HOME=%CODEX_HOME%"
if not defined SKILL_HOME set "SKILL_HOME=%USERPROFILE%\.codex"
set "SKILL_SOURCE=%~dp0..\studyhub-learning-doc\SKILL.md"
set "SKILL_DEST=%SKILL_HOME%\skills\studyhub-learning-doc"
if not exist "%SKILL_SOURCE%" (
  echo Skill source is missing. Keep the project folder intact.
  pause
  exit /b 1
)
if not exist "%SKILL_DEST%" mkdir "%SKILL_DEST%"
copy /Y "%SKILL_SOURCE%" "%SKILL_DEST%\SKILL.md" >nul
if errorlevel 1 (
  echo Installation failed. Check directory permissions.
  pause
  exit /b 1
)
echo Installed studyhub-learning-doc to "%SKILL_DEST%".
echo Restart Codex or open a new chat to use it.
pause
