@echo off
echo Запуск AI системы определения бактерий...
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

REM Запускаем приложение
echo.
echo Запуск веб-интерфейса...
echo Приложение будет доступно по адресу: http://localhost:8501
echo.
streamlit run app.py

pause
