@echo off
setlocal enabledelayedexpansion

echo ====================================
echo  Installing dependencies
echo ====================================

:: Change to script directory
cd /d "%~dp0"

:: Check for virtual environment
if not exist ".venv\" (
    echo Virtual environment not found. Creating...
    python -m venv .venv
    if errorlevel 1 (
        echo Error: failed to create virtual environment. Make sure Python is installed and added to PATH.
        pause
        exit /b 1
    )
    echo Virtual environment created.
)

:: Activate virtual environment
call .venv\Scripts\activate

:: Install dependencies if requirements.txt exists
if exist "requirements.txt" (
    echo Installing dependencies from requirements.txt...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo Error installing dependencies.
        pause
        exit /b 1
    )
    echo Dependencies installed.
) else (
    echo requirements.txt not found. Skipping dependency installation.
)

:: Django migrations
echo Applying Django migrations...
python manage.py makemigrations
if errorlevel 1 (
    echo Error while creating migrations.
    pause
    exit /b 1
)
python manage.py migrate
if errorlevel 1 (
    echo Error while applying migrations.
    pause
    exit /b 1
)
echo Migrations applied successfully.