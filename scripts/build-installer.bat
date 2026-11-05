@echo off
setlocal
cd /d "%~dp0.."
set "ISCC_PATH=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if not exist "%ISCC_PATH%" set "ISCC_PATH=%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe"
if not exist "%ISCC_PATH%" (
  echo Install Inno Setup 6 first, or run ISCC.exe installer\StudyHub.iss manually.
  pause
  exit /b 1
)
"%ISCC_PATH%" installer\StudyHub.iss
if errorlevel 1 exit /b 1
echo Installer built: installer-output\StudyHub-Setup.exe
endlocal
