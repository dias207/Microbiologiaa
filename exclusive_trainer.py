#!/usr/bin/env python3
"""
Эксклюзивная система только для ваших 20 фотографий
"""

import cv2
import numpy as np
import json
import os
from datetime import datetime
import shutil
import hashlib

class ExclusiveBacteriaTrainer:
    """Только для ваших фотографий - остальные не работают"""
    
    def __init__(self):
        self.data_dir = "exclusive_database"
        self.metadata_file = os.path.join(self.data_dir, "exclusive.json")
        self.samples = []
        self.max_samples = 20  # Максимум 20 фотографий
        
        # Создаем директорию
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(os.path.join(self.data_dir, "images"), exist_ok=True)
        
        # Загружаем существующие данные
        self.load_database()
    
    def load_database(self):
        """Загружает базу данных"""
        if os.path.exists(self.metadata_file):
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    self.samples = json.load(f)
                print(f"📁 Загружено {len(self.samples)}/{self.max_samples} эксклюзивных примеров")
            except:
                self.samples = []
        else:
            self.samples = []
    
    def save_database(self):
        """Сохраняет базу данных"""
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(self.samples, f, ensure_ascii=False, indent=2)
        print(f"💾 Сохранено {len(self.samples)}/{self.max_samples} эксклюзивных примеров")
    
    def add_exclusive_sample(self, image_path: str, family: str, genus: str, species: str, notes: str = ""):
        """Добавляет эксклюзивный пример"""
        
        if len(self.samples) >= self.max_samples:
            print(f"❌ Достигнут лимит {self.max_samples} фотографий!")
            return None
        
        # Копируем изображение
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"exclusive_{len(self.samples)+1:02d}.jpg"
        dest_path = os.path.join(self.data_dir, "images", filename)
        
        shutil.copy2(image_path, dest_path)
        
        # Создаем уникальный хэш изображения
        with open(dest_path, 'rb') as f:
            image_hash = hashlib.md5(f.read()).hexdigest()
        
        # Анализируем изображение для палочек
        image = cv2.imread(dest_path)
        bacilli_count = self.count_bacilli(image)
        
        # Извлекаем признаки
        features = self.extract_features(image)
        
        # Добавляем в базу
        sample = {
            "id": len(self.samples),
            "filename": filename,
            "hash": image_hash,
            "timestamp": timestamp,
            "taxonomy": {
                "family": family.strip(),
                "genus": genus.strip(),
                "species": species.strip()
            },
            "bacilli_count": bacilli_count,
            "features": features,
            "notes": notes.strip(),
            "exclusive": True
        }
        
        self.samples.append(sample)
        self.save_database()
        
        print(f"✅ Эксклюзивный пример #{sample['id']+1}/{self.max_samples} добавлен!")
        print(f"🏛️ {family} → {genus} → {species}")
        print(f"🦠 Палочек: {bacilli_count}")
        
        return sample
    
    def count_bacilli(self, image: np.ndarray) -> int:
        """Считает количество палочек"""
        
        # Конвертация в градации серого
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        
        # Бинаризация
        binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                     cv2.THRESH_BINARY_INV, 11, 2)
        
        # Поиск контуров
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        bacilli_count = 0
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < 10:  # Фильтруем шум
                continue
            
            # Ограничивающий прямоугольник
            rect = cv2.minAreaRect(contour)
            (width, height) = rect[1]
            
            if width > 0 and height > 0:
                aspect_ratio = max(width, height) / min(width, height)
                # Палочки имеют соотношение сторон > 2.0
                if aspect_ratio > 2.0:
                    bacilli_count += 1
        
        return bacilli_count
    
    def extract_features(self, image: np.ndarray) -> dict:
        """Извлекает признаки изображения"""
        
        # Конвертация в градации серого
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        
        features = {
            "mean_intensity": float(np.mean(gray)),
            "std_intensity": float(np.std(gray)),
            "height": image.shape[0],
            "width": image.shape[1],
            "aspect_ratio": float(image.shape[1] / image.shape[0])
        }
        
        # Анализ контуров
        contours, _ = cv2.findContours(
            cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                               cv2.THRESH_BINARY_INV, 11, 2), 
            cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        
        valid_contours = [c for c in contours if cv2.contourArea(c) > 10]
        
        if valid_contours:
            circularities = []
            for contour in valid_contours:
                area = cv2.contourArea(contour)
                perimeter = cv2.arcLength(contour, True)
                if perimeter > 0:
                    circularity = 4 * np.pi * area / (perimeter ** 2)
                    circularities.append(circularity)
            
            features.update({
                "num_contours": len(valid_contours),
                "mean_circularity": float(np.mean(circularities)) if circularities else 0
            })
        else:
            features.update({
                "num_contours": 0,
                "mean_circularity": 0
            })
        
        return features
    
    def classify_exclusive_image(self, image: np.ndarray) -> dict:
        """Классифицирует только эксклюзивные изображения"""
        
        if not self.samples:
            return {
                "Тұқымдастық": "❌ База пуста",
                "Туыстастық": "❌ База пуста", 
                "Түрі": "❌ База пуста",
                "error": "Нет эксклюзивных примеров"
            }
        
        # Извлекаем признаки текущего изображения
        current_features = self.extract_features(image)
        current_bacilli = self.count_bacilli(image)
        
        # Находим наиболее похожие примеры
        best_match = None
        best_score = 0
        
        for sample in self.samples:
            score = 0
            
            # Сравнение по палочкам (важный фактор)
            if sample["bacilli_count"] == current_bacilli:
                score += 0.4
            elif abs(sample["bacilli_count"] - current_bacilli) <= 2:
                score += 0.2
            
            # Сравнение по интенсивности (более гибко)
            intensity_diff = abs(sample["features"]["mean_intensity"] - current_features["mean_intensity"])
            if intensity_diff < 50:
                score += 0.3
            elif intensity_diff < 100:
                score += 0.2
            elif intensity_diff < 150:
                score += 0.1
            
            # Сравнение по количеству контуров (более гибко)
            contour_diff = abs(sample["features"]["num_contours"] - current_features["num_contours"])
            if contour_diff <= 50:
                score += 0.2
            elif contour_diff <= 100:
                score += 0.1
            elif contour_diff <= 200:
                score += 0.05
            
            # Сравнение по форме (круглость)
            if "mean_circularity" in sample["features"] and "mean_circularity" in current_features:
                circ_diff = abs(sample["features"]["mean_circularity"] - current_features["mean_circularity"])
                if circ_diff < 0.1:
                    score += 0.1
            
            if score > best_score:
                best_score = score
                best_match = sample
        
        # Порог схожести для эксклюзивных изображений (очень низкий для гибкости)
        if best_match and best_score > 0.1:
            tax = best_match["taxonomy"]
            confidence = min(best_score * 100, 98)
            
            return {
                "Тұқымдастық": f"{tax['family']} ({confidence:.0f}%)",
                "Туыстастық": f"{tax['genus']} ({confidence:.0f}%)",
                "Түрі": f"{tax['species']} ({confidence:.0f}%)",
                "match_id": best_match["id"],
                "confidence": confidence
            }
        else:
            return {
                "Тұқымдастық": "❌ Не определено",
                "Туыстастыґт": "❌ Не определено", 
                "Түрі": "❌ Не определено",
                "error": "Изображение не соответствует эксклюзивной базе",
                "best_score": best_score
            }
    
    def get_status(self):
        """Возвращает статус системы"""
        return {
            "total": len(self.samples),
            "max": self.max_samples,
            "remaining": self.max_samples - len(self.samples),
            "percentage": (len(self.samples) / self.max_samples) * 100,
            "ready": len(self.samples) >= 3  # Минимум 3 для работы
        }

# Глобальный эксклюзивный тренер
exclusive_trainer = ExclusiveBacteriaTrainer()

def add_exclusive_bacteria(image_path: str, family: str, genus: str, species: str, notes: str = ""):
    """Добавляет эксклюзивный пример"""
    return exclusive_trainer.add_exclusive_sample(image_path, family, genus, species, notes)

def classify_exclusive_bacteria(image: np.ndarray) -> dict:
    """Классифицирует только эксклюзивные изображения"""
    return exclusive_trainer.classify_exclusive_image(image)

def get_exclusive_status():
    """Возвращает статус эксклюзивной системы"""
    return exclusive_trainer.get_status()
