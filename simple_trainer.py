#!/usr/bin/env python3
"""
Простая система для добавления фотографий с таксономией
"""

import cv2
import numpy as np
import json
import os
from datetime import datetime
import shutil

class SimpleBacteriaTrainer:
    """Простой тренер для добавления примеров"""
    
    def __init__(self):
        self.data_dir = "bacteria_database"
        self.metadata_file = os.path.join(self.data_dir, "database.json")
        self.samples = []
        
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
                print(f"📁 Загружено {len(self.samples)} примеров")
            except:
                self.samples = []
        else:
            self.samples = []
    
    def save_database(self):
        """Сохраняет базу данных"""
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(self.samples, f, ensure_ascii=False, indent=2)
        print(f"💾 Сохранено {len(self.samples)} примеров")
    
    def add_sample(self, image_path: str, family: str, genus: str, species: str, notes: str = ""):
        """Добавляет пример в базу"""
        
        # Копируем изображение
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"bacteria_{timestamp}.jpg"
        dest_path = os.path.join(self.data_dir, "images", filename)
        
        shutil.copy2(image_path, dest_path)
        
        # Анализируем изображение для палочек
        image = cv2.imread(dest_path)
        bacilli_count = self.count_bacilli(image)
        
        # Извлекаем признаки
        features = self.extract_features(image)
        
        # Добавляем в базу
        sample = {
            "id": len(self.samples),
            "filename": filename,
            "timestamp": timestamp,
            "taxonomy": {
                "family": family.strip(),
                "genus": genus.strip(),
                "species": species.strip()
            },
            "bacilli_count": bacilli_count,
            "features": features,
            "notes": notes.strip()
        }
        
        self.samples.append(sample)
        self.save_database()
        
        print(f"✅ Добавлен пример #{sample['id']}: {family} → {genus} → {species}")
        print(f"🦠 Обнаружено палочек: {bacilli_count}")
        
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
            "width": image.shape[1]
        }
        
        return features
    
    def classify_image(self, image: np.ndarray) -> dict:
        """Классифицирует новое изображение"""
        
        if not self.samples:
            return {"Тұқымдастық": "Нет данных", "Туыстастық": "Нет данных", "Түрі": "Нет данных"}
        
        # Извлекаем признаки текущего изображения
        current_features = self.extract_features(image)
        current_bacilli = self.count_bacilli(image)
        
        # Находим наиболее похожие примеры
        best_match = None
        best_score = 0
        
        for sample in self.samples:
            score = 0
            
            # Сравнение по палочкам
            if sample["bacilli_count"] == current_bacilli:
                score += 0.4
            elif abs(sample["bacilli_count"] - current_bacilli) <= 2:
                score += 0.2
            
            # Сравнение по интенсивности
            intensity_diff = abs(sample["features"]["mean_intensity"] - current_features["mean_intensity"])
            if intensity_diff < 20:
                score += 0.3
            elif intensity_diff < 50:
                score += 0.1
            
            # Сравнение по размеру
            size_diff = abs(sample["features"]["height"] - current_features["height"])
            if size_diff < 100:
                score += 0.3
            elif size_diff < 200:
                score += 0.1
            
            if score > best_score:
                best_score = score
                best_match = sample
        
        if best_match and best_score > 0.5:
            tax = best_match["taxonomy"]
            confidence = min(best_score * 100, 95)
            
            return {
                "Тұқымдастық": f"{tax['family']} ({confidence:.0f}%)",
                "Туыстастық": f"{tax['genus']} ({confidence:.0f}%)",
                "Түрі": f"{tax['species']} ({confidence:.0f}%)"
            }
        else:
            return {
                "Тұқымдастыґт": "Не определено",
                "Туыстастық": "Не определено", 
                "Түрі": "Не определено"
            }
    
    def get_stats(self):
        """Возвращает статистику"""
        if not self.samples:
            return {"total": 0, "message": "База пуста"}
        
        families = set()
        genera = set()
        species = set()
        
        for sample in self.samples:
            tax = sample["taxonomy"]
            families.add(tax["family"])
            genera.add(tax["genus"])
            species.add(tax["species"])
        
        return {
            "total": len(self.samples),
            "families": list(families),
            "genera": list(genera),
            "species": list(species)
        }

# Глобальный тренер
trainer = SimpleBacteriaTrainer()

def add_bacteria_sample(image_path: str, family: str, genus: str, species: str, notes: str = ""):
    """Добавляет пример бактерий"""
    return trainer.add_sample(image_path, family, genus, species, notes)

def classify_bacteria_image(image: np.ndarray) -> dict:
    """Классифицирует бактерии"""
    return trainer.classify_image(image)

def get_database_stats():
    """Возвращает статистику базы"""
    return trainer.get_stats()
