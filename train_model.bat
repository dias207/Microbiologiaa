@echo off
echo Обучение модели классификации бактерий...
echo.

REM Проверяем наличие Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Ошибка: Python не установлен или не добавлен в PATH
    pause
    exit /b 1
)

REM Проверяем наличие виртуального окружения
if not exist "venv" (
    echo Создание виртуального окружения...
    python -m venv venv
)

REM Активируем виртуальное окружение
call venv\Scripts\activate.bat

REM Устанавливаем зависимости
echo Установка зависимостей...
pip install -r requirements.txt

REM Проверяем наличие данных
if not exist "data" (
    echo Ошибка: Директория 'data' не найдена!
    echo Пожалуйста, создайте директорию 'data' и добавьте обучающие изображения.
    echo Структура: data/family/genus/species/image_files
    pause
    exit /b 1
)

REM Запускаем обучение
echo.
echo Начало обучения модели...
echo.
python train.py

echo.
echo Обучение завершено!
pause
