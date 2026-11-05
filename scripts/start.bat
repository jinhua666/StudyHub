@echo off
setlocal
cd /d "%~dp0.."
if not exist "release\StudyHub\StudyHub.exe" (
  echo Desktop application is missing. Run scripts\build-desktop.bat first.
  pause
  exit /b 1
)
start "" "%~dp0..\release\StudyHub\StudyHub.exe"
endlocal
