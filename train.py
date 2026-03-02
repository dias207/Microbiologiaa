import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import torchvision.transforms as transforms
from PIL import Image
import os
import json
from typing import Dict, List, Tuple
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import matplotlib.pyplot as plt
from tqdm import tqdm

from model import BacteriaClassifier, BACTERIA_TAXONOMY, create_model
from utils import ImageProcessor

class BacteriaDataset(Dataset):
    """Класс датасета для бактерий"""
    
    def __init__(self, data_dir: str, transform=None, taxonomy_file: str = None):
        self.data_dir = data_dir
        self.transform = transform
        self.samples = []
        self.taxonomy_mapping = {}
        
        # Загружаем таксономию из файла или используем стандартную
        if taxonomy_file and os.path.exists(taxonomy_file):
            with open(taxonomy_file, 'r', encoding='utf-8') as f:
                self.taxonomy_data = json.load(f)
        else:
            self.taxonomy_data = BACTERIA_TAXONOMY
        
        # Создаем маппинг для классов
        self._create_taxonomy_mapping()
        
        # Загружаем данные
        self._load_samples()
    
    def _create_taxonomy_mapping(self):
        """Создает маппинг таксономии в индексы"""
        for level in ['families', 'genera', 'species']:
            self.taxonomy_mapping[level] = {
                name: idx for idx, name in enumerate(self.taxonomy_data[level])
            }
    
    def _load_samples(self):
        """Загружает образцы из директории"""
        # Ожидаемая структура: data_dir/family/genus/species/image.jpg
        for family in os.listdir(self.data_dir):
            family_path = os.path.join(self.data_dir, family)
            if not os.path.isdir(family_path):
                continue
                
            if family not in self.taxonomy_mapping['families']:
                continue
                
            for genus in os.listdir(family_path):
                genus_path = os.path.join(family_path, genus)
                if not os.path.isdir(genus_path):
                    continue
                    
                if genus not in self.taxonomy_mapping['genera']:
                    continue
                    
                for species in os.listdir(genus_path):
                    species_path = os.path.join(genus_path, species)
                    if not os.path.isdir(species_path):
                        continue
                        
                    if species not in self.taxonomy_mapping['species']:
                        continue
                        
                    for image_file in os.listdir(species_path):
                        if image_file.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                            image_path = os.path.join(species_path, image_file)
                            self.samples.append({
                                'path': image_path,
                                'family_idx': self.taxonomy_mapping['families'][family],
                                'genus_idx': self.taxonomy_mapping['genera'][genus],
                                'species_idx': self.taxonomy_mapping['species'][species],
                                'family_name': family,
                                'genus_name': genus,
                                'species_name': species
                            })
    
    def __len__(self):
        return len(self.samples)
    
    def __getitem__(self, idx):
        sample = self.samples[idx]
        
        # Загружаем изображение
        image = Image.open(sample['path']).convert('RGB')
        
        # Применяем трансформации
        if self.transform:
            image = self.transform(image)
        
        return {
            'image': image,
            'family': sample['family_idx'],
            'genus': sample['genus_idx'],
            'species': sample['species_idx'],
            'family_name': sample['family_name'],
            'genus_name': sample['genus_name'],
            'species_name': sample['species_name']
        }

class BacteriaTrainer:
    """Класс для обучения модели"""
    
    def __init__(self, model: BacteriaClassifier, device: str = 'cpu'):
        self.model = model
        self.device = device
        self.model.to(device)
        
        # Оптимизатор и функции потерь
        self.optimizer = optim.Adam(model.parameters(), lr=0.001, weight_decay=1e-4)
        self.family_criterion = nn.CrossEntropyLoss()
        self.genus_criterion = nn.CrossEntropyLoss()
        self.species_criterion = nn.CrossEntropyLoss()
        
        # История обучения
        self.history = {
            'train_loss': [],
            'val_loss': [],
            'train_acc': {
                'family': [],
                'genus': [],
                'species': []
            },
            'val_acc': {
                'family': [],
                'genus': [],
                'species': []
            }
        }
    
    def train_epoch(self, dataloader: DataLoader) -> Dict[str, float]:
        """Обучение одной эпохи"""
        self.model.train()
        total_loss = 0.0
        correct_predictions = {'family': 0, 'genus': 0, 'species': 0}
        total_samples = 0
        
        progress_bar = tqdm(dataloader, desc="Training")
        
        for batch in progress_bar:
            images = batch['image'].to(self.device)
            family_labels = batch['family'].to(self.device)
            genus_labels = batch['genus'].to(self.device)
            species_labels = batch['species'].to(self.device)
            
            # Обнуляем градиенты
            self.optimizer.zero_grad()
            
            # Прямой проход
            outputs = self.model(images)
            
            # Вычисляем потери
            family_loss = self.family_criterion(outputs['family'], family_labels)
            genus_loss = self.genus_criterion(outputs['genus'], genus_labels)
            species_loss = self.species_criterion(outputs['species'], species_labels)
            
            total_batch_loss = family_loss + genus_loss + species_loss
            
            # Обратный проход
            total_batch_loss.backward()
            self.optimizer.step()
            
            # Статистика
            total_loss += total_batch_loss.item()
            
            # Вычисляем точность
            _, family_pred = torch.max(outputs['family'], 1)
            _, genus_pred = torch.max(outputs['genus'], 1)
            _, species_pred = torch.max(outputs['species'], 1)
            
            correct_predictions['family'] += (family_pred == family_labels).sum().item()
            correct_predictions['genus'] += (genus_pred == genus_labels).sum().item()
            correct_predictions['species'] += (species_pred == species_labels).sum().item()
            
            total_samples += images.size(0)
            
            # Обновляем прогресс бар
            progress_bar.set_postfix({
                'loss': f'{total_batch_loss.item():.4f}',
                'f_acc': f'{correct_predictions["family"]/total_samples:.3f}',
                'g_acc': f'{correct_predictions["genus"]/total_samples:.3f}',
                's_acc': f'{correct_predictions["species"]/total_samples:.3f}'
            })
        
        avg_loss = total_loss / len(dataloader)
        accuracies = {
            level: correct / total_samples 
            for level, correct in correct_predictions.items()
        }
        
        return {'loss': avg_loss, 'accuracies': accuracies}
    
    def validate(self, dataloader: DataLoader) -> Dict[str, float]:
        """Валидация модели"""
        self.model.eval()
        total_loss = 0.0
        correct_predictions = {'family': 0, 'genus': 0, 'species': 0}
        total_samples = 0
        
        with torch.no_grad():
            for batch in tqdm(dataloader, desc="Validation"):
                images = batch['image'].to(self.device)
                family_labels = batch['family'].to(self.device)
                genus_labels = batch['genus'].to(self.device)
                species_labels = batch['species'].to(self.device)
                
                outputs = self.model(images)
                
                # Вычисляем потери
                family_loss = self.family_criterion(outputs['family'], family_labels)
                genus_loss = self.genus_criterion(outputs['genus'], genus_labels)
                species_loss = self.species_criterion(outputs['species'], species_labels)
                
                total_batch_loss = family_loss + genus_loss + species_loss
                total_loss += total_batch_loss.item()
                
                # Вычисляем точность
                _, family_pred = torch.max(outputs['family'], 1)
                _, genus_pred = torch.max(outputs['genus'], 1)
                _, species_pred = torch.max(outputs['species'], 1)
                
                correct_predictions['family'] += (family_pred == family_labels).sum().item()
                correct_predictions['genus'] += (genus_pred == genus_labels).sum().item()
                correct_predictions['species'] += (species_pred == species_labels).sum().item()
                
                total_samples += images.size(0)
        
        avg_loss = total_loss / len(dataloader)
        accuracies = {
            level: correct / total_samples 
            for level, correct in correct_predictions.items()
        }
        
        return {'loss': avg_loss, 'accuracies': accuracies}
    
    def train(self, train_loader: DataLoader, val_loader: DataLoader, 
              epochs: int = 50, save_path: str = 'best_model.pth'):
        """Основной цикл обучения"""
        best_val_loss = float('inf')
        
        print(f"Начало обучения на {epochs} эпох...")
        
        for epoch in range(epochs):
            print(f"\nЭпоха {epoch + 1}/{epochs}")
            
            # Обучение
            train_metrics = self.train_epoch(train_loader)
            
            # Валидация
            val_metrics = self.validate(val_loader)
            
            # Сохраняем историю
            self.history['train_loss'].append(train_metrics['loss'])
            self.history['val_loss'].append(val_metrics['loss'])
            
            for level in ['family', 'genus', 'species']:
                self.history['train_acc'][level].append(train_metrics['accuracies'][level])
                self.history['val_acc'][level].append(val_metrics['accuracies'][level])
            
            # Вывод статистики
            print(f"Train Loss: {train_metrics['loss']:.4f}")
            print(f"Val Loss: {val_metrics['loss']:.4f}")
            
            for level in ['family', 'genus', 'species']:
                train_acc = train_metrics['accuracies'][level]
                val_acc = val_metrics['accuracies'][level]
                print(f"{level.capitalize()} - Train Acc: {train_acc:.3f}, Val Acc: {val_acc:.3f}")
            
            # Сохраняем лучшую модель
            if val_metrics['loss'] < best_val_loss:
                best_val_loss = val_metrics['loss']
                torch.save({
                    'epoch': epoch + 1,
                    'model_state_dict': self.model.state_dict(),
                    'optimizer_state_dict': self.optimizer.state_dict(),
                    'val_loss': best_val_loss,
                    'taxonomy': BACTERIA_TAXONOMY
                }, save_path)
                print(f"Новая лучшая модель сохранена: {save_path}")
    
    def plot_training_history(self, save_path: str = 'training_history.png'):
        """Строит графики истории обучения"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # Потери
        axes[0, 0].plot(self.history['train_loss'], label='Train Loss')
        axes[0, 0].plot(self.history['val_loss'], label='Val Loss')
        axes[0, 0].set_title('Training and Validation Loss')
        axes[0, 0].set_xlabel('Epoch')
        axes[0, 0].set_ylabel('Loss')
        axes[0, 0].legend()
        
        # Точность по уровням
        for i, level in enumerate(['family', 'genus', 'species']):
            row = (i + 1) // 2
            col = (i + 1) % 2
            
            axes[row, col].plot(self.history['train_acc'][level], label=f'Train {level}')
            axes[row, col].plot(self.history['val_acc'][level], label=f'Val {level}')
            axes[row, col].set_title(f'{level.capitalize()} Accuracy')
            axes[row, col].set_xlabel('Epoch')
            axes[row, col].set_ylabel('Accuracy')
            axes[row, col].legend()
        
        plt.tight_layout()
        plt.savefig(save_path)
        plt.close()
        print(f"Графики обучения сохранены: {save_path}")

def main():
    """Главная функция для обучения"""
    # Параметры
    data_dir = 'data'  # Директория с данными
    batch_size = 32
    epochs = 50
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    
    print(f"Используемое устройство: {device}")
    
    # Трансформации для изображений
    train_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(10),
        transforms.ColorJitter(brightness=0.2, contrast=0.2),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                           std=[0.229, 0.224, 0.225])
    ])
    
    val_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                           std=[0.229, 0.224, 0.225])
    ])
    
    # Создаем датасеты
    try:
        full_dataset = BacteriaDataset(data_dir, transform=train_transform)
        print(f"Загружено {len(full_dataset)} изображений")
    except Exception as e:
        print(f"Ошибка при загрузке данных: {e}")
        print("Пожалуйста, убедитесь, что директория 'data' существует и имеет правильную структуру")
        return
    
    # Разделяем на обучающую и валидационную выборки
    train_indices, val_indices = train_test_split(
        range(len(full_dataset)), test_size=0.2, random_state=42
    )
    
    train_dataset = torch.utils.data.Subset(full_dataset, train_indices)
    val_dataset = torch.utils.data.Subset(full_dataset, val_indices)
    
    # Обновляем трансформации для валидационного датасета
    val_dataset.dataset.transform = val_transform
    
    # Создаем загрузчики данных
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
    
    # Создаем модель и тренер
    model = create_model()
    trainer = BacteriaTrainer(model, device)
    
    # Обучаем модель
    trainer.train(train_loader, val_loader, epochs)
    
    # Строим графики
    trainer.plot_training_history()
    
    print("Обучение завершено!")

if __name__ == "__main__":
    main()
