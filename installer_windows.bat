@echo off
setlocal enabledelayedexpansion

echo ====================================
echo  Установка зависимостей и настройка
echo ====================================

:: Переходим в папку скрипта
cd /d "%~dp0"

:: Проверяем наличие виртуального окружения
if not exist "venv\" (
    echo Виртуальное окружение не найдено. Создаём...
    python -m venv venv
    if errorlevel 1 (
        echo Ошибка: не удалось создать виртуальное окружение. Убедитесь, что Python установлен.
        pause
        exit /b 1
    )
    echo Виртуальное окружение создано.
)

:: Активируем виртуальное окружение
call venv\Scripts\activate

:: Устанавливаем зависимости, если есть requirements.txt
if exist "requirements.txt" (
    echo Устанавливаем зависимости из requirements.txt...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo Ошибка при установке зависимостей.
        pause
        exit /b 1
    )
    echo Зависимости установлены.
) else (
    echo Файл requirements.txt не найден. Пропускаем установку зависимостей.
)
