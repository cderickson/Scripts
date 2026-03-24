@echo off
setlocal EnableDelayedExpansion
REM Run from this script's folder (so paths work when double-clicked or run from elsewhere)
cd /d "%~dp0"

echo.
echo === zip-mtgo-logs build ===
echo Folder: %CD%
echo.

REM When you double-click a .bat, Explorer often does NOT use the same PATH as your terminal.
REM Try the Python launcher first (usually works if Python is installed from python.org).
set "PYEXE="
where py >nul 2>&1 && set "PYEXE=py -3"
if not defined PYEXE where python >nul 2>&1 && set "PYEXE=python"
if not defined PYEXE (
  echo ERROR: Python was not found.
  echo Install Python from https://www.python.org/ and tick "Add python.exe to PATH",
  echo   or ensure the "py" launcher is available.
  echo.
  pause
  exit /b 1
)

echo Using: %PYEXE%
echo.

REM Trailing spaces after ^ break line continuation — keep lines clean.
%PYEXE% -m PyInstaller --console --onefile --clean --noconfirm --noupx -i "auxiliary\icon_1.png" zip-mtgo-logs.py
if errorlevel 1 (
  echo.
  echo PyInstaller failed. If you see "No module named PyInstaller", run:  pip install pyinstaller
  echo.
  pause
  exit /b 1
)

if exist "dist\zip-mtgo-logs.exe" (
  move /y "dist\zip-mtgo-logs.exe" ".\zip-mtgo-logs.exe"
) else (
  echo ERROR: dist\zip-mtgo-logs.exe was not created.
  pause
  exit /b 1
)

if exist build rmdir build /s /q
if exist zip-mtgo-logs.spec del zip-mtgo-logs.spec
if exist dist rmdir dist /s /q

echo.
echo Done. Output: %CD%\zip-mtgo-logs.exe
echo.
REM Pause when double-clicked (no args) so the window stays open to read messages
if "%~1"=="" pause
exit /b 0
