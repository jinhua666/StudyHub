@echo off
setlocal
cd /d "%~dp0.."
if not exist "backend\.venv\Scripts\python.exe" (
  echo Please install dependencies as described in README.md first.
  pause
  exit /b 1
)
start "StudyHub API" cmd /k "cd /d "%~dp0..\backend" && .venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"
cd /d "%~dp0..\frontend"
call npm run dev
endlocal
