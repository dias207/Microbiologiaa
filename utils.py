import cv2
import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image
import matplotlib.pyplot as plt
from typing import Tuple, List, Dict, Any
import torchvision.transforms as transforms
from model import BACTERIA_TAXONOMY
from exclusive_trainer import classify_exclusive_bacteria, get_exclusive_status

class BacilliDetector:
    """Детектор палочковидных бактерий"""
    
    def __init__(self):
        self.min_aspect_ratio = 1.5  # Уменьшили минимальное соотношение сторон
        self.min_length = 8  # Уменьшили минимальную длину палочки
        self.max_length = 100  # Максимальная длина палочки
        self.min_width = 1  # Уменьшили минимальную ширину
        
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Предобработка изображения для детекции"""
        # Конвертация в градации серого
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
            
        # Применение гауссового размытия для уменьшения шума
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Адаптивная бинаризация
        binary = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY_INV, 11, 2
        )
        
        # Морфологические операции для очистки
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        cleaned = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
        
        return cleaned
    
    def detect_bacilli(self, image: np.ndarray) -> Tuple[List[Dict], int]:
        """Детекция палочковидных бактерий"""
        processed = self.preprocess_image(image)
        
        # Поиск контуров
        contours, _ = cv2.findContours(
            processed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        
        bacilli = []
        
        for contour in contours:
            # Получаем ограничивающий прямоугольник
            rect = cv2.minAreaRect(contour)
            box = cv2.boxPoints(rect)
            box = np.array(box, dtype=np.int32)
            
            # Вычисляем размеры
            width = min(rect[1][0], rect[1][1])
            height = max(rect[1][0], rect[1][1])
            
            # Проверяем соотношение сторон и размеры
            if height > 0:
                aspect_ratio = height / width
                
                if (aspect_ratio >= self.min_aspect_ratio and 
                    self.min_length <= height <= self.max_length and
                    width >= self.min_width):
                    
                    # Вычисляем площадь и центр
                    area = cv2.contourArea(contour)
                    M = cv2.moments(contour)
                    if M["m00"] != 0:
                        cx = int(M["m10"] / M["m00"])
                        cy = int(M["m01"] / M["m00"])
                    else:
                        cx, cy = 0, 0
                    
                    bacilli.append({
                        'contour': contour,
                        'box': box,
                        'center': (cx, cy),
                        'length': height,
                        'width': width,
                        'aspect_ratio': aspect_ratio,
                        'area': area
                    })
        
        return bacilli, len(bacilli)
    
    def draw_bacilli(self, image: np.ndarray, bacilli: List[Dict]) -> np.ndarray:
        """Отрисовка обнаруженных палочек на изображении"""
        result = image.copy()
        
        for i, bacillus in enumerate(bacilli):
            # Рисуем ограничивающую рамку
            cv2.drawContours(result, [bacillus['box']], 0, (0, 255, 0), 2)
            
            # Рисуем центр
            cv2.circle(result, bacillus['center'], 3, (255, 0, 0), -1)
            
            # Добавляем номер
            cv2.putText(result, str(i+1), 
                       (bacillus['center'][0] - 10, bacillus['center'][1] - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        
        return result

class ImageProcessor:
    """Класс для обработки изображений"""
    
    def __init__(self):
        self.transform = transforms.Compose([
            transforms.Resize(224),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])
    
    def preprocess_for_model(self, image: np.ndarray) -> torch.Tensor:
        """Предобработка для модели классификации"""
        if len(image.shape) == 3:
            # Конвертация BGR в RGB
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        else:
            image_rgb = image
            
        # Конвертируем в PIL Image
        pil_image = Image.fromarray(image_rgb)
            
        # Применяем трансформации
        tensor = self.transform(pil_image)
        return tensor.unsqueeze(0)
    
    def load_image(self, image_path: str) -> np.ndarray:
        """Загрузка изображения"""
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Не удалось загрузить изображение: {image_path}")
        return image

def heuristic_classification(image: np.ndarray, bacilli_count: int) -> Dict[str, torch.Tensor]:
    """Эвристическая классификация на основе характеристик изображения"""
    
    # Анализ характеристик изображения
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
    
    # Вычисляем статистики
    mean_intensity = np.mean(gray)
    std_intensity = np.std(gray)
    
    # Анализ формы бактерий
    contours, _ = cv2.findContours(
        cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                           cv2.THRESH_BINARY_INV, 11, 2), 
        cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    
    total_contours = len(contours)
    circular_contours = 0
    elongated_contours = 0
    
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 10:  # Фильтруем шум
            perimeter = cv2.arcLength(contour, True)
            if perimeter > 0:
                circularity = 4 * np.pi * area / (perimeter ** 2)
                if circularity > 0.7:  # Круглые формы
                    circular_contours += 1
                elif circularity < 0.3:  # Вытянутые формы
                    elongated_contours += 1
    
    # Эвристические правила для классификации
    if bacilli_count > 10:
        # Много палочек - вероятно Bacillaceae
        family_idx = 4  # Bacillaceae
        genus_idx = 3   # Bacillus
        species_idx = 4 # B. subtilis
    elif circular_contours > elongated_contours and circular_contours > 5:
        # Преобладание кокков - Staphylococcaceae
        family_idx = 3  # Staphylococcaceae
        genus_idx = 0   # Staphylococcus
        species_idx = 1 # S. aureus
    elif mean_intensity < 100:
        # Темные бактерии - Enterobacteriaceae
        family_idx = 1  # Enterobacteriaceae
        genus_idx = 1   # Escherichia
        species_idx = 2 # E. coli
    else:
        # По умолчанию - Streptococcaceae
        family_idx = 2  # Streptococcaceae
        genus_idx = 2   # Streptococcus
        species_idx = 3 # S. pyogenes
    
    # Создаем тензоры с softmax вероятностями
    num_families = len(BACTERIA_TAXONOMY['families'])
    num_genera = len(BACTERIA_TAXONOMY['genera'])
    num_species = len(BACTERIA_TAXONOMY['species'])
    
    # Генерируем вероятности с преобладанием предсказанного класса
    family_probs = torch.ones(num_families) * 0.05
    family_probs[family_idx] = 0.8
    
    genus_probs = torch.ones(num_genera) * 0.05
    genus_probs[genus_idx] = 0.8
    
    species_probs = torch.ones(num_species) * 0.05
    species_probs[species_idx] = 0.8
    
    # Нормализуем
    family_probs = family_probs / family_probs.sum()
    genus_probs = genus_probs / genus_probs.sum()
    species_probs = species_probs / species_probs.sum()
    
    return {
        'family': family_probs.unsqueeze(0),
        'genus': genus_probs.unsqueeze(0),
        'species': species_probs.unsqueeze(0)
    }

def smart_classification(image: np.ndarray, bacilli_count: int) -> Dict[str, str]:
    """Эксклюзивная классификация только на ваших фотографиях"""
    
    # Проверяем статус эксклюзивной системы
    status = get_exclusive_status()
    
    if status["ready"]:
        # Используем эксклюзивную базу
        result = classify_exclusive_bacteria(image)
        print(f"🔒 Эксклюзивная классификация: {status['total']}/{status['max']} примеров")
        
        # Если есть ошибка, показываем ее
        if "error" in result:
            print(f"❌ {result['error']}")
        
        return result
    else:
        # Система не готова
        return {
            "Тұқымдастыґт": f"❌ Нужно {3-status['total']} примеров",
            "Туыстастыґт": f"❌ Нужно {3-status['total']} примеров",
            "Түрі": f"❌ Нужно {3-status['total']} примеров",
            "error": f"Добавьте еще {3-status['total']} примеров для работы"
        }

def format_taxonomy_prediction(predictions: Dict[str, torch.Tensor], 
                            taxonomy_dict: Dict[str, List[str]]) -> Dict[str, str]:
    """Форматирует предсказания в читаемый вид"""
    result = {}
    
    for level, pred_tensor in predictions.items():
        if level == 'family':
            taxonomy_list = taxonomy_dict['families']
            label = "Тұқымдастық"
        elif level == 'genus':
            taxonomy_list = taxonomy_dict['genera']
            label = "Туыстастық"
        elif level == 'species':
            taxonomy_list = taxonomy_dict['species']
            label = "Түрі"
        else:
            continue
            
        # Получаем индекс максимального значения
        predicted_idx = torch.argmax(pred_tensor, dim=1).item()
        predicted_class = taxonomy_list[predicted_idx]
        
        # Получаем вероятность
        probability = pred_tensor[0][predicted_idx].item()
        
        result[label] = f"{predicted_class} ({probability:.2%})"
    
    return result
