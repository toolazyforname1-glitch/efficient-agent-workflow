@echo off
setlocal EnableExtensions DisableDelayedExpansion
set "ROOT=%~dp0"
set "PYEXE="

rem 1) Preferred: bundled py-tui venv, one level up from Tempt3
if exist "%ROOT%..\tools\py-tui\Scripts\python.exe" set "PYEXE=%ROOT%..\tools\py-tui\Scripts\python.exe"
if defined PYEXE goto :have_python

rem 2) python on PATH
for /f "delims=" %%P in ('where python 2^>nul') do if not defined PYEXE set "PYEXE=%%P"
if defined PYEXE goto :have_python

rem 3) py -3, resolved to its real interpreter path
for /f "delims=" %%P in ('py -3 -c "import sys; print(sys.executable)" 2^>nul') do if not defined PYEXE set "PYEXE=%%P"
if defined PYEXE goto :have_python

echo [install] ERROR: no Python interpreter found.
echo [install] Install Python 3.10+ or create tools\py-tui, then retry.
exit /b 1

:have_python
echo [install] Python: %PYEXE%

rem Verify Textual is importable - never auto-install
"%PYEXE%" -c "import textual" >nul 2>&1
if errorlevel 1 (
  echo [install] ERROR: Textual is not installed for this interpreter.
  echo [install] Fix: "%PYEXE%" -m pip install -r "%ROOT%installer\requirements.txt"
  exit /b 1
)

set "TUI=%ROOT%installer\questionnaire.py"
if not exist "%TUI%" (
  echo [install] ERROR: missing %TUI%
  exit /b 1
)

echo [install] Launching questionnaire in a new minimized window...
echo [install] Rules: 15 named rules, all selected by default.
echo [install] Output: %ROOT%output\agents-md-addendum.md  or  %ROOT%output\skill\SKILL.md
echo [install] Exit: q / Esc / Ctrl+C, or close the TUI window.
powershell -NoProfile -Command "$q=[char]34; Start-Process -FilePath $env:PYEXE -ArgumentList ($q + $env:TUI + $q) -WorkingDirectory $env:ROOT -WindowStyle Minimized"
if errorlevel 1 (
  echo [install] ERROR: could not start the TUI window.
  exit /b 1
)
echo [install] Started.
exit /b 0
