# 🚀 Быстрый старт

## Минимальные требования
- Python 3.8+
- 4GB RAM
- Windows/Linux/macOS

## 🖱️ Запуск в один клик (Windows)

### 1. Запуск приложения
```bash
run_app.bat
```

### 2. Создание демо-изображения
```bash
cd examples
python demo_image.py
```

## 🐧 Linux/macOS

### 1. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 2. Запуск приложения
```bash
streamlit run app.py
```

## 📸 Тестирование без данных

Приложение работает без обученной модели и демонстрирует:
- Загрузку изображений
- Детекцию палочек через OpenCV
- Интерфейс в фирменном стиле

## 🎯 Для полноценной работы

1. **Подготовьте данные** в директории `data/`:
   ```
   data/
   ├── Micrococaceae/
   │   └── Staphylococcus/
   │       ├── S. epidermidis/
   │       └── S. aureus/
   └── Enterobacteriaceae/
       └── Escherichia/
           └── E. coli/
   ```

2. **Обучите модель**:
   ```bash
   train_model.bat  # Windows
   # или
   python train.py   # Linux/macOS
   ```

3. **Получите файл** `best_model.pth` в корне проекта

## 🔧 Возможные проблемы

### Ошибка: ModuleNotFoundError
```bash
pip install -r requirements.txt
```

### Ошибка: CUDA out of memory
- Приложение автоматически переключается на CPU
- Уменьшите размер изображения

### Медленная работа
- Используйте изображения до 1000x1000 пикселей
- Закройте другие приложения

## 📱 Доступ к приложению

После запуска откройте в браузере:
**http://localhost:8501**

---

🧬 *Проект готов к демонстрации на Анамедфоруме!*
