@echo off
cd /d "%~dp0"

echo ========================================================
echo   University Project - Quick Start
echo ========================================================
echo.

if not exist "venv\Scripts\activate.bat" (
    echo Virtual environment not found. Running full setup first...
    call setup_and_run.bat
    exit /b
)

echo Opening browser: http://127.0.0.1:8000/
start "" "http://127.0.0.1:8000/"

call .\venv\Scripts\activate.bat
python manage.py runserver 127.0.0.1:8000
pause
