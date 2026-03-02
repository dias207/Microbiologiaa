#!/usr/bin/env python3
"""
Добавление примеров бактерий в базу данных
"""

from simple_trainer import add_bacteria_sample, get_database_stats
import os

def add_bacteria_examples():
    """Добавляет примеры бактерий"""
    
    print("🧬 Добавление примеров бактерий в базу данных")
    print("=" * 50)
    
    # Получаем текущую статистику
    stats = get_database_stats()
    print(f"📊 Текущее количество примеров: {stats.get('total', 0)}")
    
    print("\n📸 Добавьте фотографии бактерий:")
    print("1. Поместите изображение в папку проекта")
    print("2. Укажите точную таксономию")
    print("3. Я добавлю пример в базу")
    
    # Примеры для добавления (замените на реальные пути)
    examples = [
        # Пример 1: S. aureus
        {
            "image_path": "staph_aureus_1.jpg",
            "family": "Staphylococcaceae",
            "genus": "Staphylococcus", 
            "species": "S. aureus",
            "notes": "Золотистый стафилококк, грамположительный"
        },
        # Пример 2: E. coli
        {
            "image_path": "e_coli_1.jpg", 
            "family": "Enterobacteriaceae",
            "genus": "Escherichia",
            "species": "E. coli",
            "notes": "Кишечная палочка, грамотрицательная"
        },
        # Пример 3: B. subtilis
        {
            "image_path": "bacillus_subtilis_1.jpg",
            "family": "Bacillaceae", 
            "genus": "Bacillus",
            "species": "B. subtilis",
            "notes": "Сенная палочка, спорообразующая"
        }
    ]
    
    print(f"\n🎯 Готов добавить {len(examples)} примеров:")
    for i, ex in enumerate(examples, 1):
        print(f"{i}. {ex['family']} → {ex['genus']} → {ex['species']}")
        print(f"   Файл: {ex['image_path']}")
        print(f"   Примечания: {ex['notes']}")
        print()
    
    # Ждем реальные файлы от пользователя
    print("📤 Отправьте мне фотографии с таксономией в формате:")
    print("   - Файл: path/to/image.jpg")
    print("   - Семейство: Staphylococcaceae")
    print("   - Род: Staphylococcus")
    print("   - Вид: S. aureus")
    print("   - Примечания: (опционально)")

def add_single_example(image_path: str, family: str, genus: str, species: str, notes: str = ""):
    """Добавляет один пример"""
    
    if not os.path.exists(image_path):
        print(f"❌ Файл не найден: {image_path}")
        return False
    
    try:
        sample = add_bacteria_sample(image_path, family, genus, species, notes)
        
        print(f"✅ Успешно добавлен пример:")
        print(f"   📁 ID: #{sample['id']}")
        print(f"   🏛️ Семейство: {sample['taxonomy']['family']}")
        print(f"   🔬 Род: {sample['taxonomy']['genus']}")
        print(f"   🧬 Вид: {sample['taxonomy']['species']}")
        print(f"   🦠 Палочек: {sample['bacilli_count']}")
        print(f"   📝 Примечания: {sample['notes']}")
        
        # Показываем обновленную статистику
        stats = get_database_stats()
        print(f"\n📊 Всего в базе: {stats['total']} примеров")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка добавления: {e}")
        return False

if __name__ == "__main__":
    add_bacteria_examples()
