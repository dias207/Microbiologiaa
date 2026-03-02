import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io
import base64

from exclusive_trainer import classify_exclusive_bacteria, get_exclusive_status

def main():
    """Главная функция эксклюзивного приложения"""
    
    # Настройка страницы
    st.set_page_config(
        page_title="🦠 Эксклюзивная Система Бактерий",
        page_icon="🧬",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Заголовок
    st.markdown("""
    <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #6B46C1, #9333EA); color: white; border-radius: 10px; margin-bottom: 20px;">
        <h1 style="margin: 0;">🦠 Эксклюзивная Система Определения Бактерий</h1>
        <p style="margin: 0; font-size: 18px;">Только 19 видов бактерий • Точность до 98% • Защита от чужих фото</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Статус системы
    status = get_exclusive_status()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📁 База данных", f"{status['total']}/20")
    
    with col2:
        st.metric("📈 Прогресс", f"{status['percentage']:.0f}%")
    
    with col3:
        st.metric("✅ Готовность", "ДА" if status['ready'] else "НЕТ")
    
    # Загрузка изображения
    st.markdown("---")
    st.subheader("📸 Загрузите изображение бактерии")
    
    uploaded_file = st.file_uploader(
        "Выберите файл изображения",
        type=['jpg', 'jpeg', 'png'],
        help="Загрузите микроскопическое изображение для анализа"
    )
    
    if uploaded_file is not None:
        try:
            # Чтение изображения
            image_bytes = uploaded_file.read()
            image = Image.open(io.BytesIO(image_bytes))
            image_array = np.array(image)
            
            # Конвертация в BGR для OpenCV
            if len(image_array.shape) == 3:
                image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
            else:
                image_array = image_array
            
            # Классификация
            with st.spinner("🔍 Анализ изображения..."):
                result = classify_exclusive_bacteria(image_array)
            
            # Отображение результатов
            st.markdown("---")
            st.subheader("🧬 Результаты анализа")
            
            if "error" in result:
                st.error(f"❌ {result['error']}")
                st.info(f"🔍 Best Score: {result.get('best_score', 0):.2f}")
            else:
                # Успешная классификация
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### 🏛️ Таксономия")
                    st.success(f"**Семейство:** {result['Тұқымдастық']}")
                    st.success(f"**Род:** {result['Туыстастық']}")
                    st.success(f"**Вид:** {result['Түрі']}")
                
                with col2:
                    st.markdown("### 📊 Статистика")
                    st.info(f"**Match ID:** {result['match_id']}")
                    st.info(f"**Уверенность:** {result['confidence']:.0f}%")
                    st.info(f"**🦠 Палочки:** {result.get('bacilli_count', 'Не определено')}")
            
            # Отображение изображения
            st.markdown("---")
            st.subheader("📸 Загруженное изображение")
            st.image(image, caption="Исходное изображение", use_column_width=True)
            
        except Exception as e:
            st.error(f"❌ Ошибка обработки: {e}")
    
    else:
        # Инструкция
        st.markdown("---")
        st.subheader("ℹ️ Информация о системе")
        
        st.markdown("""
        ### 🎯 Особенности:
        - **🔒 Эксклюзивная база:** Только 19 определенных бактерий
        - **🎯 Точность:** 20-98% на обученных данных  
        - **❌ Защита:** Посторонние изображения отклоняются
        - **🦠 Авто-анализ:** Определение количества палочек
        
        ### 📋 Список бактерий:
        1. S. aureus - гроздевидные кокки
        2. N. meningitidis - диплококки
        3. V. cholerae - изогнутые запятые
        4. S. pyogenes - цепочки кокков
        5. B. melitensis - очень мелкие кокки
        6. E. coli - кишечные палочки
        7. B. anthracis - крупные палочки со спорами
        8. C. tetani - палочки с терминальными спорами
        9. C. jejuni - S-образные изогнутые палочки
        10. S. dysenteriae - шигеллез
        11. F. tularensis - очень мелкие коккобактерии
        12. Y. pestis - чумные палочки
        13. L. interrogans - тонкие спиралевидные
        14. M. leprae - проказа
        15. C. botulinum - ботулизм
        16. H. pylori - хеликобактериоз
        17. S. typhi - брюшной тиф
        18. N. gonorrhoeae - гонорея
        19. C. perfringens - газовая гангрена
        
        ### 🚀 Как использовать:
        1. Загрузите изображение бактерии
        2. Получите таксономию или ошибку
        3. Попробуйте загрузить СВОЕ фото - увидите защиту
        """)
    
    # Футер
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 10px; background-color: #f0f2f1; color: white; border-radius: 5px;">
        <p style="margin: 0;">🏥 Разработано для Анамедфорума • 🦠 Эксклюзивная система • 🎯 Точность 98%</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
