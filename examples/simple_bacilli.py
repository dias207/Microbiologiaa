#!/usr/bin/env python3
"""
Создание простого тестового изображения с явными палочками
"""

import cv2
import numpy as np
import os

def create_simple_bacilli_image(width=400, height=300, save_path='examples/simple_bacilli.jpg'):
    """Создает простое изображение с явными палочками"""
    
    # Белый фон
    image = np.ones((height, width, 3), dtype=np.uint8) * 255
    
    # Рисуем явные палочки
    # Палочка 1 - горизонтальная
    cv2.ellipse(image, (100, 100), (30, 8), 0, 0, 360, (100, 50, 50), -1)
    
    # Палочка 2 - вертикальная
    cv2.ellipse(image, (200, 150), (8, 35), 0, 0, 360, (120, 60, 60), -1)
    
    # Палочка 3 - диагональная
    cv2.ellipse(image, (300, 200), (25, 6), 45, 0, 360, (110, 55, 55), -1)
    
    # Палочка 4 - еще одна диагональная
    cv2.ellipse(image, (150, 250), (20, 5), -30, 0, 360, (105, 52, 52), -1)
    
    # Палочка 5 - короткая горизонтальная
    cv2.ellipse(image, (250, 80), (15, 4), 0, 0, 360, (115, 58, 58), -1)
    
    # Палочка 6 - длинная вертикальная
    cv2.ellipse(image, (350, 150), (6, 40), 0, 0, 360, (95, 48, 48), -1)
    
    # Добавляем несколько круглых бактерий для контраста
    cv2.circle(image, (80, 200), 8, (150, 100, 100), -1)
    cv2.circle(image, (320, 100), 10, (140, 90, 90), -1)
    cv2.circle(image, (180, 180), 7, (145, 95, 95), -1)
    
    # Сохраняем изображение
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    cv2.imwrite(save_path, image)
    
    print(f"Простое тестовое изображение сохранено: {save_path}")
    print("Изображение содержит 6 явных палочек и 3 кокка")
    
    return image

if __name__ == "__main__":
    create_simple_bacilli_image()
