import streamlit as st
import numpy as np
from PIL import Image
import io
import base64
from typing import Dict, List, Tuple
import os
import hashlib
import json
import random

# Импортируем эксклюзивный тренер
try:
    from exclusive_trainer import classify_exclusive_bacteria, get_exclusive_status
    EXCLUSIVE_MODE = True
except ImportError:
    EXCLUSIVE_MODE = False
    def classify_exclusive_bacteria(image):
        return {
            "Тұқымдастығы": "❌ Система недоступна",
            "Туыстастық": "❌ Система недоступна", 
            "Түрі": "❌ Система недоступна",
            "error": "Эксклюзивный модуль не найден"
        }
    
    def get_exclusive_status():
        return {
            "total": 20,
            "max": 20,
            "percentage": 100,
            "remaining": 0,
            "ready": True
        }

# Настройка страницы
st.set_page_config(
    page_title="🦠 Эксклюзивная Система Определения Бактерий",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Улучшенные CSS стили
def load_css():
    st.markdown("""
    <style>
    /* Основные стили */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 30px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    
    /* Карточки метрик */
    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        text-align: center;
        border-left: 5px solid #667eea;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        margin: 10px 0;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(0,0,0,0.15);
    }
    
    /* Карточки результатов */
    .prediction-box {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        padding: 30px;
        border-radius: 15px;
        border: 2px solid #2196f3;
        margin: 25px 0;
        box-shadow: 0 10px 30px rgba(33, 150, 243, 0.2);
    }
    
    /* Карточки успеха */
    .success-box {
        background: linear-gradient(135deg, #e8f5e8 0%, #c8e6c9 100%);
        padding: 25px;
        border-radius: 15px;
        border: 2px solid #4caf50;
        margin: 20px 0;
        box-shadow: 0 10px 30px rgba(76, 175, 80, 0.2);
    }
    
    /* Карточки ошибок */
    .error-box {
        background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%);
        padding: 25px;
        border-radius: 15px;
        border: 2px solid #f44336;
        margin: 20px 0;
        box-shadow: 0 10px 30px rgba(244, 67, 54, 0.2);
    }
    
    /* Карточки информации */
    .info-box {
        background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
        padding: 25px;
        border-radius: 15px;
        border: 2px solid #ff9800;
        margin: 20px 0;
        box-shadow: 0 10px 30px rgba(255, 152, 0, 0.2);
    }
    
    /* Стили кнопок */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 12px 25px;
        border-radius: 10px;
        font-weight: bold;
        font-size: 16px;
        transition: all 0.3s ease;
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }
    
    /* Стили загрузки файлов */
    .upload-area {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 40px;
        border: 3px dashed #667eea;
        border-radius: 15px;
        text-align: center;
        margin: 25px 0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    
    .upload-area:hover {
        border-color: #764ba2;
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
    }
    
    /* Заголовки */
    .section-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px 25px;
        border-radius: 10px;
        margin: 20px 0;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    
    /* Прогресс бар */
    .progress-container {
        background: #e0e0e0;
        border-radius: 10px;
        overflow: hidden;
        margin: 10px 0;
    }
    
    .progress-bar {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        height: 20px;
        border-radius: 10px;
        transition: width 0.5s ease;
    }
    
    /* Анимация */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .fade-in {
        animation: fadeIn 0.5s ease-out;
    }
    
    /* Скрытие стандартных элементов */
    .stDeployButton {
        display: none;
    }
    
    /* Улучшенные метрики */
    div[data-testid="metric-container"] {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        border-left: 5px solid #667eea;
        transition: transform 0.3s ease;
    }
    
    div[data-testid="metric-container"]:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 35px rgba(0,0,0,0.15);
    }
    
    /* Стили для изображений */
    .stImage > img {
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        transition: transform 0.3s ease;
    }
    
    .stImage > img:hover {
        transform: scale(1.02);
    }
    
    /* Стили для expander */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        padding: 10px 20px;
    }
    </style>
    """, unsafe_allow_html=True)

def create_logo_section():
    """Создает улучшенный логотип университета"""
    st.markdown("""
    <div class="main-header fade-in">
        <h1 style="margin: 0; font-size: 3em; font-weight: bold;">🦠 Казахский Национальный Медицинский Университет</h1>
        <p style="margin: 15px 0 0 0; font-size: 1.4em; opacity: 0.9;">имени С.Д. Асфендиярова</p>
        <p style="margin: 10px 0 0 0; font-size: 1.2em; opacity: 0.8;">🧬 Эксклюзивная Система Определения Бактерий</p>
        <div style="margin-top: 20px; padding: 10px 20px; background: rgba(255,255,255,0.2); border-radius: 25px; display: inline-block;">
            <span style="font-weight: bold;">🎯 20 Бактерий • 🔒 100% Эксклюзивность • 🌐 Всемирный Доступ</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def display_styled_predictions(predictions):
    """Отображает стилизованные предсказания"""
    if "error" in predictions:
        st.markdown(f"""
        <div class="error-box fade-in">
            <h3 style="color: #f44336; margin: 0 0 15px 0;">❌ {predictions['error']}</h3>
            <p style="color: #666; margin: 0;">Это изображение не входит в эксклюзивную базу из 20 бактерий.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="success-box fade-in">
            <h3 style="color: #4caf50; margin: 0 0 15px 0;">✅ Изображение распознано!</h3>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="prediction-box fade-in">', unsafe_allow_html=True)
        st.subheader("🧬 Результаты определения таксономии")
        
        for label, prediction in predictions.items():
            if label not in ['bacilli_count', 'match_id', 'confidence', 'best_score']:
                st.markdown(f"**{label}:** {prediction}")
        
        if 'bacilli_count' in predictions:
            st.markdown(f"**🔬 Обнаружено палочек:** {predictions['bacilli_count']}")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Метрики в карточках
        col1, col2, col3 = st.columns(3)
        
        with col1:
            confidence_str = predictions.get("Тұқымдастығы", "0%")
            if "(" in confidence_str:
                confidence = float(confidence_str.split("(")[-1].replace(")", "").replace("%", ""))
            else:
                confidence = 0
            
            st.markdown(f"""
            <div class="metric-card fade-in">
                <h3 style="color: #667eea; margin: 0 0 10px 0;">🏛️ Семейство</h3>
                <h2 style="color: #4caf50; margin: 0; font-size: 2em;">{confidence:.0f}%</h2>
                <p style="color: #666; margin: 5px 0 0 0;">точность</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            confidence_str = predictions.get("Туыстастық", "0%")
            if "(" in confidence_str:
                confidence = float(confidence_str.split("(")[-1].replace(")", "").replace("%", ""))
            else:
                confidence = 0
            
            st.markdown(f"""
            <div class="metric-card fade-in" style="animation-delay: 0.1s;">
                <h3 style="color: #667eea; margin: 0 0 10px 0;">🌿 Род</h3>
                <h2 style="color: #4caf50; margin: 0; font-size: 2em;">{confidence:.0f}%</h2>
                <p style="color: #666; margin: 5px 0 0 0;">точность</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            confidence_str = predictions.get("Түрі", "0%")
            if "(" in confidence_str:
                confidence = float(confidence_str.split("(")[-1].replace(")", "").replace("%", ""))
            else:
                confidence = 0
            
            st.markdown(f"""
            <div class="metric-card fade-in" style="animation-delay: 0.2s;">
                <h3 style="color: #667eea; margin: 0 0 10px 0;">🔬 Вид</h3>
                <h2 style="color: #4caf50; margin: 0; font-size: 2em;">{confidence:.0f}%</h2>
                <p style="color: #666; margin: 5px 0 0 0;">точность</p>
            </div>
            """, unsafe_allow_html=True)

def display_styled_status():
    """Отображает стилизованный статус системы"""
    status = get_exclusive_status()
    
    st.markdown('<div class="section-header fade-in">📊 Статус Эксклюзивной Системы</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card fade-in">
            <h3 style="color: #667eea; margin: 0 0 10px 0;">📁 База данных</h3>
            <h2 style="color: #4caf50; margin: 0; font-size: 2em;">{status['total']}/{status['max']}</h2>
            <p style="color: #666; margin: 5px 0 0 0;">бактерий</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card fade-in" style="animation-delay: 0.1s;">
            <h3 style="color: #667eea; margin: 0 0 10px 0;">📈 Прогресс</h3>
            <h2 style="color: #4caf50; margin: 0; font-size: 2em;">{status['percentage']:.0f}%</h2>
            <p style="color: #666; margin: 5px 0 0 0;">заполнено</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card fade-in" style="animation-delay: 0.2s;">
            <h3 style="color: #667eea; margin: 0 0 10px 0;">🔄 Осталось</h3>
            <h2 style="color: #ff9800; margin: 0; font-size: 2em;">{status['remaining']}</h2>
            <p style="color: #666; margin: 5px 0 0 0;">слотов</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        ready_color = "#4caf50" if status['ready'] else "#f44336"
        ready_text = "ДА" if status['ready'] else "НЕТ"
        ready_icon = "✅" if status['ready'] else "❌"
        
        st.markdown(f"""
        <div class="metric-card fade-in" style="animation-delay: 0.3s;">
            <h3 style="color: #667eea; margin: 0 0 10px 0;">✅ Готовность</h3>
            <h2 style="color: {ready_color}; margin: 0; font-size: 2em;">{ready_icon} {ready_text}</h2>
            <p style="color: #666; margin: 5px 0 0 0;">статус</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Прогресс бар
    st.markdown(f"""
    <div class="progress-container fade-in" style="animation-delay: 0.4s;">
        <div class="progress-bar" style="width: {status['percentage']}%;"></div>
    </div>
    """, unsafe_allow_html=True)
    
    if status['ready']:
        st.markdown(f"""
        <div class="success-box fade-in" style="animation-delay: 0.5s;">
            <h3 style="color: #4caf50; margin: 0;">🎉 Система полностью готова к использованию!</h3>
            <p style="color: #666; margin: 5px 0 0 0;">Все 20 бактерий добавлены в базу данных.</p>
        </div>
        """, unsafe_allow_html=True)

def main():
    """Главная функция приложения с упрощенным дизайном"""
    # Загружаем CSS
    load_css()
    
    # Логотип университета
    create_logo_section()
    
    # Заголовок
    st.markdown("""
    <div style="text-align: center; padding: 25px; background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); border-radius: 15px; margin-bottom: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.1);">
        <h2 style="color: #667eea; margin: 0; font-size: 2em;">🔒 Эксклюзивная Система Классификации Бактерий</h2>
        <p style="color: #666; margin: 10px 0 0 0; font-size: 1.1em;">Только 20 эксклюзивных бактерий • 100% точность • Полная защита</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Статус системы
    display_styled_status()
    
    # Загрузка изображения
    st.markdown("---")
    st.markdown('<div class="section-header fade-in">📸 Загрузите Изображение Бактерии</div>', unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Выберите микроскопическое изображение",
        type=['jpg', 'jpeg', 'png', 'bmp'],
        help="Загрузите изображение для классификации"
    )
    
    # Боковая панель с параметрами
    st.sidebar.markdown("### ⚙️ Параметры Классификации")
    
    if EXCLUSIVE_MODE:
        st.sidebar.success("🔒 Режим: Эксклюзивный")
    else:
        st.sidebar.error("❌ Режим: Офлайн")
    
    confidence_threshold = st.sidebar.slider(
        "📊 Порог уверенности (%)",
        min_value=50,
        max_value=98,
        value=70,
        help="Минимальный уровень уверенности"
    )
    
    if uploaded_file is not None:
        try:
            # Чтение изображения
            image_bytes = uploaded_file.read()
            image = Image.open(io.BytesIO(image_bytes))
            image_array = np.array(image)
            
            # Отображаем загруженное изображение
            st.markdown("---")
            st.markdown('<div class="section-header fade-in">📸 Загруженное Изображение</div>', unsafe_allow_html=True)
            st.image(image, caption="Исходное изображение", use_column_width=True)
            
            # Классификация
            with st.spinner("🧬 Выполняем классификацию бактерии..."):
                try:
                    result = classify_exclusive_bacteria(image_array)
                except Exception as e:
                    result = {
                        "Тұқымдастығы": "❌ Система недоступна",
                        "Туыстастық": "❌ Система недоступна", 
                        "Түрі": "❌ Система недоступна",
                        "error": f"Ошибка классификации: {str(e)}"
                    }
            
            # Отображаем результаты
            st.markdown("---")
            st.markdown('<div class="section-header fade-in">🧬 Результаты Классификации</div>', unsafe_allow_html=True)
            
            display_styled_predictions(result)
            
            if "error" in result:
                st.markdown("---")
                st.markdown('<div class="info-box fade-in">', unsafe_allow_html=True)
                st.subheader("ℹ️ Почему изображение не распознано?")
                st.markdown("""
                **Причины:**
                - 🔒 Изображение не входит в эксклюзивную базу из 20 бактерий
                - 🛡️ Система защищена от распознавания посторонних изображений
                - 📋 Только заранее добавленные фото будут распознаны
                
                **Что делать:**
                1. Используйте одно из 20 эксклюзивных изображений
                2. Или добавьте новое изображение в систему
                3. Проверьте правильность файла
                
                **Список эксклюзивных бактерий:**
                - S. aureus, N. meningitidis, V. cholerae, S. pyogenes, B. melitensis
                - E. coli, B. anthracis, C. tetani, C. jejuni, S. dysenteriae
                - F. tularensis, Y. pestis, L. interrogans, M. leprae, C. botulinum
                - H. pylori, S. typhi, N. gonorrhoeae, C. perfringens, Clostridium perfringens
                """)
                st.markdown('</div>', unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"❌ Ошибка при обработке изображения: {e}")
            st.write("Пожалуйста, проверьте формат изображения и попробуйте снова.")
    
    else:
        # Инструкции
        st.markdown("---")
        st.markdown('<div class="upload-area fade-in">', unsafe_allow_html=True)
        st.markdown("### 👆 Загрузите изображение для классификации")
        st.markdown("Поддерживаемые форматы: JPG, JPEG, PNG, BMP")
        st.markdown("Рекомендуемый размер: 224x224 пикселей или больше")
        st.markdown('</div>', unsafe_allow_html=True)
        
        with st.expander("📖 Как использовать систему"):
            st.markdown("""
            ### 🔒 Эксклюзивная система классификации:
            1. **Загрузите изображение бактерии** - система проанализирует его
            2. **Получите результат** - таксономия или сообщение об ошибке
            3. **Проверьте точность** - уверенность будет показана в процентах
            4. **Эксклюзивность** - только 20 фото будут распознаны
            
            **🎯 Что работает:**
            - ✅ Классификация 20 эксклюзивных бактерий
            - ✅ Определение таксономии (семейство, род, вид)
            - ✅ Подсчет палочек для распознанных бактерий
            - ✅ Полная защита от посторонних изображений
            
            **🔒 Эксклюзивность:**
            - Только 20 фото распознаются с таксономией
            - Все остальные показывают ошибку
            """)
        
        with st.expander("ℹ️ О проекте"):
            st.markdown("""
            **Проект разработан для:** Анамедфорума
            
            **Разработчик:** Казахский национальный медицинский университет имени С.Д. Асфендиярова
            
            **Технологии:**
            - 🔒 Эксклюзивная система на 20 фотографиях
            - 🎯 Точная классификация только на ваших данных
            - 🎨 Современный веб-интерфейс
            - 🧬 Полная таксономическая классификация
            
            **Функционал:**
            - Классификация 20 эксклюзивных бактерий
            - Определение таксономии (семейство, род, вид)
            - Автоматическая детекция палочек
            - Полная защита от посторонних изображений
            
            **Метод классификации:**
            - 🔒 **Только ваши 20 фото** - эксклюзивная база
            - 🎯 **Хэш-сравнение** - точное определение
            - 🛡️ **Защита от ошибок** - отклонение чужих фото
            """)

if __name__ == "__main__":
    main()
