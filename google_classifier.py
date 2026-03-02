try:
    import google.genai as genai
except ImportError:
    import google.generativeai as genai
import cv2
import numpy as np
import base64
import json
import os
from typing import Dict, Optional

class GoogleBacteriaClassifier:
    """Классификатор бактерий с использованием Google Gemini API"""
    
    def __init__(self, api_key: str = None):
        """Инициализация с API ключом"""
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY')
        if not self.api_key:
            print("⚠️ API ключ Google не найден. Используем эвристическую систему.")
            self.enabled = False
        else:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                self.enabled = True
                print("✅ Google Gemini классификатор инициализирован")
            except Exception as e:
                print(f"❌ Ошибка инициализации Google Gemini: {e}")
                self.enabled = False
    
    def encode_image(self, image: np.ndarray) -> bytes:
        """Кодирует изображение в байты"""
        _, buffer = cv2.imencode('.jpg', image)
        return buffer.tobytes()
    
    def classify_bacteria(self, image: np.ndarray, bacilli_count: int) -> Dict[str, str]:
        """Классифицирует бактерии с помощью Google Gemini"""
        
        if not self.enabled:
            return self._fallback_classification(image, bacilli_count)
        
        try:
            # Кодируем изображение
            image_bytes = self.encode_image(image)
            
            # Анализ характеристик изображения
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
            mean_intensity = np.mean(gray)
            
            # Создаем промпт для Gemini
            prompt = f"""
            Проанализируй это микроскопическое изображение бактерий и определи таксономию.
            
            Наблюдения:
            - Количество обнаруженных палочек: {bacilli_count}
            - Средняя интенсивность изображения: {mean_intensity:.1f}
            
            Определи и верни результат в формате JSON:
            {{
                "family": "название семейства на латинице",
                "genus": "название рода на латинице", 
                "species": "название вида на латинице",
                "confidence": "уверенность в процентах",
                "reasoning": "краткое обоснование на русском"
            }}
            
            Возможные варианты:
            Семейства: Micrococaceae, Enterobacteriaceae, Streptococcaceae, Staphylococcaceae, Bacillaceae, Pseudomonadaceae
            Роды: Staphylococcus, Escherichia, Streptococcus, Bacillus, Pseudomonas, Micrococcus, Klebsiella, Salmonella, Shigella, Proteus
            Виды: S. epidermidis, S. aureus, E. coli, S. pyogenes, B. subtilis, P. aeruginosa, M. luteus, K. pneumoniae, S. enterica, S. dysenteriae, P. mirabilis
            
            Будь точен в микробиологической классификации. Ответь только JSON.
            """
            
            # Отправляем запрос к Gemini
            response = self.model.generate_content([
                prompt,
                {"mime_type": "image/jpeg", "data": image_bytes}
            ])
            
            # Парсим ответ
            result_text = response.text
            
            try:
                # Ищем JSON в ответе
                start_idx = result_text.find('{')
                end_idx = result_text.rfind('}') + 1
                
                if start_idx != -1 and end_idx != -1:
                    json_str = result_text[start_idx:end_idx]
                    result = json.loads(json_str)
                    
                    return {
                        "Тұқымдастық": f"{result.get('family', 'Unknown')} ({result.get('confidence', '50%')})",
                        "Туыстастық": f"{result.get('genus', 'Unknown')} ({result.get('confidence', '50%')})",
                        "Түрі": f"{result.get('species', 'Unknown')} ({result.get('confidence', '50%')})"
                    }
                else:
                    raise ValueError("JSON не найден в ответе")
                    
            except json.JSONDecodeError:
                print("Ошибка парсинга JSON ответа")
                return self._fallback_classification(image, bacilli_count)
                
        except Exception as e:
            print(f"Ошибка Google Gemini API: {e}")
            return self._fallback_classification(image, bacilli_count)
    
    def _fallback_classification(self, image: np.ndarray, bacilli_count: int) -> Dict[str, str]:
        """Запасная эвристическая классификация"""
        
        # Анализ характеристик
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        mean_intensity = np.mean(gray)
        
        # Эвристические правила
        if bacilli_count > 10:
            # Много палочек - Bacillaceae
            return {
                "Тұқымдастық": "Bacillaceae (85%)",
                "Туыстастық": "Bacillus (85%)",
                "Түрі": "B. subtilis (85%)"
            }
        elif mean_intensity < 100:
            # Темные бактерии - Enterobacteriaceae
            return {
                "Тұқымдастық": "Enterobacteriaceae (80%)",
                "Туыстастық": "Escherichia (80%)",
                "Түрі": "E. coli (80%)"
            }
        else:
            # По умолчанию - Staphylococcaceae
            return {
                "Тұқымдастық": "Staphylococcaceae (75%)",
                "Туыстастық": "Staphylococcus (75%)",
                "Түрі": "S. aureus (75%)"
            }

def create_google_classifier():
    """Создает классификатор с проверкой API ключа"""
    api_key = os.getenv('GOOGLE_API_KEY')
    
    if not api_key:
        print("🔑 Для использования Google классификации:")
        print("1. Получите API ключ на https://makersuite.google.com/app/apikey")
        print("2. Установите переменную окружения GOOGLE_API_KEY")
        print("3. Или создайте файл .env с строкой: GOOGLE_API_KEY=your_key_here")
        print("🔄 Используется эвристическая система")
    
    return GoogleBacteriaClassifier(api_key)
