@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

echo ========================================================
echo   University Project - Auto Setup and Launch
echo ========================================================
echo.

:: 1. Check Python installation
where python >nul 2>nul
if %errorlevel% neq 0 (
    where py >nul 2>nul
    if %errorlevel% neq 0 (
        echo [ERROR] Python is not installed or not added to PATH.
        echo Please download and install Python from https://www.python.org/
        echo (IMPORTANT: Make sure to check "Add Python to PATH" during installation)
        echo.
        pause
        exit /b 1
    ) else (
        set PYTHON_CMD=py
    )
) else (
    set PYTHON_CMD=python
)

echo [OK] Python detected:
%PYTHON_CMD% --version
echo.

:: 2. Check and create virtual environment if missing
if not exist "venv\Scripts\activate.bat" (
    echo [1/4] Creating virtual environment (venv)...
    %PYTHON_CMD% -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created.
) else (
    echo [1/4] Virtual environment already exists.
)
echo.

:: 3. Install dependencies from requirements.txt
echo [2/4] Checking and installing packages from requirements.txt...
call .\venv\Scripts\pip.exe install -r requirements.txt --disable-pip-version-check
if %errorlevel% neq 0 (
    echo [WARNING] Encountered issues with some packages. Continuing...
)
echo.

:: 4. Database migrations & sample data check
echo [3/4] Checking database...
call .\venv\Scripts\python.exe manage.py migrate --no-input

if not exist "db.sqlite3" (
    echo Seeding sample demo data (teachers, students, quiz, viva)...
    call .\venv\Scripts\python.exe populate_sample_data.py
)
echo.

:: 5. Open browser & run server
echo [4/4] Starting web server...
echo.
echo Opening browser: http://127.0.0.1:8000/
echo.
echo ========================================================
echo Login Credentials:
echo   - Teacher:   username='teacher'   password='pass123'
echo   - Student 1: username='student1'  password='pass123'
echo   - Student 2: username='student2'  password='pass123'
echo ========================================================
echo Press Ctrl + C in this window to stop the server.
echo.

start "" "http://127.0.0.1:8000/"
call .\venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000

pause
