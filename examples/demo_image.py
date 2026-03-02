#!/usr/bin/env python3
"""
Скрипт для создания демонстрационного изображения бактерий
"""

import cv2
import numpy as np
import os
from PIL import Image, ImageDraw, ImageFont
import random

def create_bacteria_demo_image(width=800, height=600, save_path='examples/demo_bacteria.jpg'):
    """Создает демонстрационное изображение с бактериями"""
    
    # Создаем белое изображение
    image = np.ones((height, width, 3), dtype=np.uint8) * 255
    
    # Добавляем фон (слегка серый для микроскопического эффекта)
    background = np.random.normal(240, 5, image.shape)
    image = np.clip(image * 0.9 + background * 0.1, 0, 255).astype(np.uint8)
    
    # Рисуем кокки (круглые бактерии)
    def draw_coccus(img, center, radius, color_variation=None):
        if color_variation is None:
            color_variation = random.randint(-20, 20)
        
        color = (150 + color_variation, 100 + color_variation, 100 + color_variation)
        cv2.circle(img, center, radius, color, -1)
        # Добавляем границу
        cv2.circle(img, center, radius, (80, 50, 50), 1)
        # Добавляем текстуру
        for _ in range(3):
            offset_x = random.randint(-radius//2, radius//2)
            offset_y = random.randint(-radius//2, radius//2)
            cv2.circle(img, 
                      (center[0] + offset_x, center[1] + offset_y), 
                      radius//4, 
                      (180 + color_variation, 130 + color_variation, 130 + color_variation), 
                      -1)
    
    # Рисуем палочки (бациллы)
    def draw_bacillus(img, start, end, width, color_variation=None):
        if color_variation is None:
            color_variation = random.randint(-20, 20)
        
        color = (120 + color_variation, 80 + color_variation, 80 + color_variation)
        
        # Рисуем эллипс
        center = ((start[0] + end[0]) // 2, (start[1] + end[1]) // 2)
        length = int(np.sqrt((end[0] - start[0])**2 + (end[1] - start[1])**2))
        angle = np.arctan2(end[1] - start[1], end[0] - start[0]) * 180 / np.pi
        
        # Создаем маску для эллипса
        mask = np.zeros_like(img)
        cv2.ellipse(mask, center, (length//2, width), angle, 0, 360, color, -1)
        cv2.ellipse(mask, center, (length//2, width), angle, 0, 360, (60, 40, 40), 1)
        
        # Добавляем маску к изображению
        img = cv2.addWeighted(img, 1, mask, 0.8, 0)
        
        return img
    
    # Генерируем бактерии
    bacteria_positions = []
    
    # Добавляем группы кокков (гроздья) - меньше для разнообразия
    for _ in range(2):
        center_x = random.randint(100, max(width - 100, 150))
        center_y = random.randint(100, max(height - 100, 150))
        
        # Создаем гроздь из 4-6 кокков
        cluster_size = random.randint(4, 6)
        for i in range(cluster_size):
            angle = 2 * np.pi * i / cluster_size + random.uniform(-0.3, 0.3)
            radius = random.randint(15, 20)
            x = center_x + int(radius * 1.2 * np.cos(angle))
            y = center_y + int(radius * 1.2 * np.sin(angle))
            
            if 0 < x < width and 0 < y < height:
                draw_coccus(image, (x, y), random.randint(6, 10))
                bacteria_positions.append(('coccus', (x, y)))
    
    # Добавляем больше палочек для тестирования детекции
    for _ in range(25):  # Увеличили количество палочек
        x1 = random.randint(50, max(width - 50, 100))
        y1 = random.randint(50, max(height - 50, 100))
        
        # Создаем палочки разной ориентации
        angle = random.uniform(0, 2 * np.pi)
        length = random.randint(25, 45)  # Увеличили длину
        width = random.randint(3, 6)
        
        x2 = x1 + int(length * np.cos(angle))
        y2 = y1 + int(length * np.sin(angle))
        
        if (0 < x1 < width and 0 < y1 < height and 
            0 < x2 < width and 0 < y2 < height):
            image = draw_bacillus(image, (x1, y1), (x2, y2), width)
            bacteria_positions.append(('bacillus', ((x1 + x2)//2, (y1 + y2)//2)))
    
    # Добавляем отдельные кокки
    for _ in range(15):  # Уменьшили количество кокков
        x = random.randint(50, max(width - 50, 100))
        y = random.randint(50, max(height - 50, 100))
        draw_coccus(image, (x, y), random.randint(5, 8))
        bacteria_positions.append(('coccus', (x, y)))
    
    # Добавляем шум и артефакты для реалистичности
    noise = np.random.normal(0, 3, image.shape)
    image = np.clip(image + noise, 0, 255).astype(np.uint8)
    
    # Добавляем размытие для микроскопического эффекта
    image = cv2.GaussianBlur(image, (1, 1), 0.5)
    
    # Сохраняем изображение
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    cv2.imwrite(save_path, image)
    
    print(f"Демонстрационное изображение сохранено: {save_path}")
    print(f"Создано бактерий: {len(bacteria_positions)}")
    print(f"Палочек: {sum(1 for t, _ in bacteria_positions if t == 'bacillus')}")
    print(f"Кокков: {sum(1 for t, _ in bacteria_positions if t == 'coccus')}")
    
    return image

if __name__ == "__main__":
    # Создаем директорию для примеров
    os.makedirs('examples', exist_ok=True)
    
    # Создаем демонстрационное изображение
    demo_image = create_bacteria_demo_image()
    
    print("\nДемонстрационное изображение создано!")
    print("Используйте его для тестирования приложения.")
    print("Путь: examples/demo_bacteria.jpg")
