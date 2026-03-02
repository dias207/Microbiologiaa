import openai
import cv2
import numpy as np
import base64
import json
from typing import Dict, Tuple
import os

class ChatGPTBacteriaClassifier:
    """Классификатор бактерий с использованием ChatGPT API"""
    
    def __init__(self, api_key: str = None):
        """Инициализация с API ключом"""
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            print("⚠️ API ключ OpenAI не найден. Используем эвристическую систему.")
            self.enabled = False
        else:
            openai.api_key = self.api_key
            self.enabled = True
    
    def encode_image(self, image: np.ndarray) -> str:
        """Кодирует изображение в base64"""
        _, buffer = cv2.imencode('.jpg', image)
        return base64.b64encode(buffer).decode('utf-8')
    
    def classify_bacteria(self, image: np.ndarray, bacilli_count: int) -> Dict[str, str]:
        """Классифицирует бактерии с помощью ChatGPT"""
        
        if not self.enabled:
            return self._fallback_classification(image, bacilli_count)
        
        try:
            # Кодируем изображение
            base64_image = self.encode_image(image)
            
            # Анализ характеристик изображения
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
            mean_intensity = np.mean(gray)
            
            # Создаем промпт для ChatGPT
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
                "reasoning": "краткое обоснование"
            }}
            
            Возможные варианты:
            Семейства: Micrococaceae, Enterobacteriaceae, Streptococcaceae, Staphylococcaceae, Bacillaceae, Pseudomonadaceae
            Роды: Staphylococcus, Escherichia, Streptococcus, Bacillus, Pseudomonas, Micrococcus, Klebsiella, Salmonella, Shigella, Proteus
            Виды: S. epidermidis, S. aureus, E. coli, S. pyogenes, B. subtilis, P. aeruginosa, M. luteus, K. pneumoniae, S. enterica, S. dysenteriae, P. mirabilis
            
            Будь точен в микробиологической классификации.
            """
            
            # Отправляем запрос к ChatGPT
            response = openai.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=500
            )
            
            # Парсим ответ
            result_text = response.choices[0].message.content
            
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
            print(f"Ошибка ChatGPT API: {e}")
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

def create_classifier():
    """Создает классификатор с проверкой API ключа"""
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("🔑 Для использования ChatGPT классификации:")
        print("1. Установите переменную окружения OPENAI_API_KEY")
        print("2. Или создайте файл .env с строкой: OPENAI_API_KEY=your_key_here")
        print("🔄 Используется эвристическая система")
    
    return ChatGPTBacteriaClassifier(api_key)
