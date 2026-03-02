#!/usr/bin/env python3
"""
Простая публикация через LocalTunnel
"""

import subprocess
import time
import threading
import sys

def run_streamlit():
    """Запускает Streamlit"""
    print("🚀 Запускаем Streamlit...")
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", "app.py", 
        "--server.port", "8501"
    ])

def run_localtunnel():
    """Запускает LocalTunnel"""
    time.sleep(3)  # Ждем запуска Streamlit
    print("🔗 Создаем публичную ссылку...")
    result = subprocess.run([
        "npx", "localtunnel", "--port", "8501"
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Система опубликована!")
        # Ищем URL в выводе
        for line in result.stdout.split('\n'):
            if 'your url is:' in line.lower():
                url = line.split('your url is:')[-1].strip()
                print(f"🌐 Публичная ссылка: {url}")
                print(f"📋 Поделитесь с друзьями: {url}")
                break
    else:
        print("❌ Ошибка LocalTunnel")
        print("💡 Убедитесь что Node.js установлен")

def main():
    """Основная функция"""
    print("🌐 Публикация эксклюзивной системы определения бактерий")
    print("=" * 50)
    
    # Запускаем Streamlit в фоновом потоке
    streamlit_thread = threading.Thread(target=run_streamlit)
    streamlit_thread.daemon = True
    streamlit_thread.start()
    
    # Запускаем туннель
    run_localtunnel()

if __name__ == "__main__":
    main()
