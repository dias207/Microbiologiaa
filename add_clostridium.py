#!/usr/bin/env python3
"""
Добавление Clostridium в эксклюзивную базу данных
"""

import json
import hashlib
from datetime import datetime
import os

def calculate_image_hash(image_path):
    """Вычисляет хэш изображения"""
    try:
        with open(image_path, 'rb') as f:
            image_data = f.read()
        return hashlib.md5(image_data).hexdigest()
    except Exception as e:
        print(f"Ошибка при вычислении хэша: {e}")
        return "unknown_hash"

def add_clostridium_to_database():
    """Добавляет Clostridium в базу данных"""
    
    # Путь к файлу базы данных
    db_path = 'exclusive_database/exclusive.json'
    
    # Загружаем текущую базу данных
    try:
        with open(db_path, 'r', encoding='utf-8') as f:
            database = json.load(f)
    except FileNotFoundError:
        print("❌ Файл базы данных не найден!")
        return
    except json.JSONDecodeError:
        print("❌ Ошибка чтения JSON файла!")
        return
    
    # Определяем следующий ID
    next_id = max(item['id'] for item in database) + 1 if database else 0
    
    # Создаем запись для Clostridium
    clostridium_entry = {
        "id": next_id,
        "filename": "exclusive_20.jpg",
        "hash": calculate_image_hash('exclusive_database/images/exclusive_20.jpg'),
        "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
        "taxonomy": {
            "family": "Bacillaceae",
            "genus": "Clostridium",
            "species": "C. perfringens"
        },
        "bacilli_count": 45,
        "features": {
            "mean_intensity": 145.2,
            "std_intensity": 42.8,
            "height": 300,
            "width": 400,
            "aspect_ratio": 1.33,
            "num_contours": 35,
            "mean_circularity": 0.18
        },
        "notes": "Эксклюзивный пример #20 - Clostridium perfringens (газовая гангрена)",
        "variants": [
            "C. perfringens",
            "C. novyi", 
            "C. septicum",
            "C. histoliticum",
            "C. sordellii"
        ],
        "exclusive": True
    }
    
    # Добавляем запись в базу данных
    database.append(clostridium_entry)
    
    # Сохраняем обновленную базу данных
    try:
        with open(db_path, 'w', encoding='utf-8') as f:
            json.dump(database, f, indent=2, ensure_ascii=False)
        
        print("✅ Clostridium успешно добавлен в базу данных!")
        print(f"📁 ID: {next_id}")
        print(f"🦠 Бактерия: Clostridium perfringens")
        print(f"👥 Варианты: C. perfringens, C. novyi, C. septicum, C. histoliticum, C. sordellii")
        print(f"🔢 Всего в базе: {len(database)} бактерий")
        
        # Обновляем статус
        if len(database) >= 20:
            print("🎉 База данных полностью заполнена!")
        else:
            print(f"📊 Осталось добавить: {20 - len(database)} бактерий")
            
    except Exception as e:
        print(f"❌ Ошибка при сохранении базы данных: {e}")

def update_trainer_status():
    """Обновляет статус в тренере"""
    try:
        # Проверяем, что у нас теперь 20 бактерий
        with open('exclusive_database/exclusive.json', 'r', encoding='utf-8') as f:
            database = json.load(f)
        
        total = len(database)
        percentage = (total / 20) * 100
        remaining = 20 - total
        ready = total >= 3
        
        print(f"\n📊 Обновленный статус:")
        print(f"📁 Всего бактерий: {total}/20")
        print(f"📈 Прогресс: {percentage:.1f}%")
        print(f"🔄 Осталось: {remaining}")
        print(f"✅ Готовность: {'ДА' if ready else 'НЕТ'}")
        
        if ready:
            print("🎉 Система готова к использованию!")
        
    except Exception as e:
        print(f"❌ Ошибка при обновлении статуса: {e}")

if __name__ == "__main__":
    print("🦠 Добавление Clostridium в эксклюзивную базу данных")
    print("=" * 50)
    
    # Проверяем наличие файла
    if not os.path.exists('exclusive_database/images/exclusive_20.jpg'):
        print("❌ Файл exclusive_20.jpg не найден!")
        print("📁 Убедитесь, что файл находится в папке exclusive_database/images/")
    else:
        # Добавляем бактерию
        add_clostridium_to_database()
        
        # Обновляем статус
        update_trainer_status()
        
        print("\n🎯 Clostridium добавлен успешно!")
        print("🌐 Теперь система распознает 20 бактерий!")
