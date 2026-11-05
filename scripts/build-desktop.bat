@echo off
setlocal
cd /d "%~dp0.."
if not exist "backend\.venv\Scripts\python.exe" (
  echo Create backend virtual environment and install dependencies first. See README.md.
  pause
  exit /b 1
)
if not exist "frontend\dist\index.html" (
  echo Build the frontend first: cd frontend ^&^& npm install ^&^& npm run build
  pause
  exit /b 1
)
backend\.venv\Scripts\python.exe -m PyInstaller --noconfirm --distpath release StudyHub.spec
if errorlevel 1 exit /b 1
echo Desktop application built in release\StudyHub\StudyHub.exe
endlocal
