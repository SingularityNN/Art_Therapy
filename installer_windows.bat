@echo off
setlocal enabledelayedexpansion

echo ====================================
echo  Installing dependancies
echo ====================================

:: Change to script directory
cd /d "%~dp0"

:: Проверяем наличие py.exe (Python Launcher)
where py >nul 2>nul
if errorlevel 1 (
    echo Python Launcher (py.exe) не найден. Убедитесь, что Python установлен.
    echo Скачайте Python с python.org и при установке отметьте "Add Python to PATH".
    pause
    exit /b 1
)

:: Check for virtual environment
if not exist ".venv\" (
    echo Virtual environment not found. Creating...
    py -m venv .venv
    if errorlevel 1 (
        echo Error: failed to create virtual environment. Make sure Python is installed.
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