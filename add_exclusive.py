#!/usr/bin/env python3
"""
Добавление 20 эксклюзивных фотографий
"""

from exclusive_trainer import add_exclusive_bacteria, get_exclusive_status
import os

def show_status():
    """Показывает текущий статус"""
    status = get_exclusive_status()
    print("🔒 ЭКСКЛЮЗИВНАЯ СИСТЕМА ОПРЕДЕЛЕНИЯ БАКТЕРИЙ")
    print("=" * 50)
    print(f"📊 Статус: {status['total']}/{status['max']} фотографий")
    print(f"📈 Прогресс: {status['percentage']:.1f}%")
    print(f"🔄 Осталось: {status['remaining']} фотографий")
    print(f"✅ Готовность: {'ДА' if status['ready'] else 'НЕТ'}")
    print()

def add_exclusive_sample(image_path: str, family: str, genus: str, species: str, notes: str = ""):
    """Добавляет эксклюзивный пример"""
    
    if not os.path.exists(image_path):
        print(f"❌ Файл не найден: {image_path}")
        return False
    
    try:
        sample = add_exclusive_bacteria(image_path, family, genus, species, notes)
        
        if sample:
            print(f"✅ Эксклюзивный пример #{sample['id']+1} добавлен!")
            print(f"🏛️ {family} → {genus} → {species}")
            print(f"🦠 Палочек: {sample['bacilli_count']}")
            print(f"📝 {notes}")
            print()
            
            # Показываем обновленный статус
            show_status()
            return True
        else:
            print("❌ Не удалось добавить пример")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def ready_for_20_photos():
    """Готовность к приему 20 фотографий"""
    
    print("🎯 ГОТОВНОСТЬ К ПРИЕМУ 20 ЭКСКЛЮЗИВНЫХ ФОТОГРАФИЙ")
    print("=" * 60)
    print()
    print("📸 Отправляйте фотографии в формате:")
    print("   1. Файл изображения")
    print("   2. Таксономия:")
    print("      - Семейство (Family)")
    print("      - Род (Genus)")
    print("      - Вид (Species)")
    print("   3. Примечания (опционально)")
    print()
    print("🔒 ПРАВИЛА:")
    print("   • Максимум 20 фотографий")
    print("   • Только ваши изображения будут работать")
    print("   • Все остальные фото будут давать ошибку")
    print("   • Чем больше примеров, тем точнее")
    print()
    print("🎯 ПРИМЕР:")
    print("   📸 Файл: my_bacteria_1.jpg")
    print("   🏛️ Семейство: Staphylococcaceae")
    print("   🔬 Род: Staphylococcus")
    print("   🧬 Вид: S. aureus")
    print("   📝 Примечания: Золотистый стафилококк")
    print()
    
    show_status()

if __name__ == "__main__":
    ready_for_20_photos()
