#!/usr/bin/env python3
"""
Публикация эксклюзивной системы определения бактерий через ngrok
"""

import streamlit.web.cli as stcli
import subprocess
import time
import threading
from pyngrok import ngrok

def run_streamlit():
    """Запускает Streamlit приложение"""
    try:
        stcli.main([
            "run",
            "app.py",
            "--server.port",
            "8501",
            "--server.headless",
            "true"
        ])
    except Exception as e:
        print(f"❌ Ошибка запуска Streamlit: {e}")

def main():
    """Основная функция публикации"""
    print("🚀 Запускаем публикацию эксклюзивной системы...")
    
    # Запускаем Streamlit в отдельном потоке
    streamlit_thread = threading.Thread(target=run_streamlit)
    streamlit_thread.daemon = True
    streamlit_thread.start()
    
    # Ждем запуска Streamlit
    time.sleep(5)
    
    try:
        # Создаем ngrok туннель
        print("🔗 Создаем публичную ссылку...")
        public_url = ngrok.connect(8501)
        
        print("✅ Система опубликована!")
        print(f"🌐 Публичная ссылка: {public_url}")
        print(f"🔗 Прямая ссылка: {public_url}")
        print()
        print("📋 Поделитесь этой ссылкой с друзьями:")
        print(f"   {public_url}")
        print()
        print("🛡️ Ваша эксклюзивная система доступна всем!")
        print("🦠 Только ваши 19 бактерий будут распознаваться")
        print("❌ Все остальные фото покажут ошибку")
        print()
        print("⏹️ Нажмите Ctrl+C для остановки")
        
        # Держим туннель активным
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Останавливаем публикацию...")
            
    except Exception as e:
        print(f"❌ Ошибка создания туннеля: {e}")
        print("💡 Альтернатива: используйте localtunnel")
        print("   команда: npx localtunnel --port 8501")

if __name__ == "__main__":
    main()
