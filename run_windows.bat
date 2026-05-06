@echo off
setlocal

cd /d "%~dp0"

where py >nul 2>nul
if %errorlevel%==0 (
    set "PY=py -3"
) else (
    set "PY=python"
)

if not exist ".venv\Scripts\python.exe" (
    echo Creating virtual environment...
    %PY% -m venv .venv
    if errorlevel 1 goto error
)

echo Installing dependencies...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto error

echo Starting Streamlit dashboard...
".venv\Scripts\python.exe" -m streamlit run streamlit_app.py
if errorlevel 1 goto error

goto end

:error
echo.
echo Failed to start the dashboard. Please check Python installation and network connection.
pause

:end
endlocal
