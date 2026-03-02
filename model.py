import torch
import torch.nn as nn
import torchvision.models as models
from typing import Dict, Tuple

class BacteriaClassifier(nn.Module):
    def __init__(self, num_families: int, num_genera: int, num_species: int):
        super(BacteriaClassifier, self).__init__()
        
        # Используем ResNet18 как основу
        self.backbone = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)
        
        # Замораживаем первые слои для transfer learning
        for param in list(self.backbone.parameters())[:-10]:
            param.requires_grad = False
            
        # Получаем количество признаков из последнего слоя
        num_features = self.backbone.fc.in_features
        
        # Удаляем последний слой ResNet
        self.backbone.fc = nn.Identity()
        
        # Создаем классификаторы для каждого уровня таксономии
        self.family_classifier = nn.Sequential(
            nn.Linear(num_features, 512),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(512, num_families)
        )
        
        self.genus_classifier = nn.Sequential(
            nn.Linear(num_features, 512),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(512, num_genera)
        )
        
        self.species_classifier = nn.Sequential(
            nn.Linear(num_features, 512),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(512, num_species)
        )
    
    def forward(self, x: torch.Tensor) -> Dict[str, torch.Tensor]:
        # Получаем признаки из ResNet
        features = self.backbone(x)
        
        # Получаем предсказания для каждого уровня
        family_pred = self.family_classifier(features)
        genus_pred = self.genus_classifier(features)
        species_pred = self.species_classifier(features)
        
        return {
            'family': family_pred,
            'genus': genus_pred,
            'species': species_pred
        }
    
    def get_features(self, x: torch.Tensor) -> torch.Tensor:
        """Метод для получения признаков для Grad-CAM"""
        return self.backbone(x)

# Словари с таксономией (расширенные)
BACTERIA_TAXONOMY = {
    'families': [
        'Micrococaceae', 'Enterobacteriaceae', 'Streptococcaceae', 
        'Staphylococcaceae', 'Bacillaceae', 'Pseudomonadaceae'
    ],
    'genera': [
        'Staphylococcus', 'Escherichia', 'Streptococcus', 
        'Bacillus', 'Pseudomonas', 'Micrococcus', 'Klebsiella',
        'Salmonella', 'Shigella', 'Proteus'
    ],
    'species': [
        'S. epidermidis', 'S. aureus', 'E. coli', 'S. pyogenes', 
        'B. subtilis', 'P. aeruginosa', 'M. luteus', 'K. pneumoniae',
        'S. enterica', 'S. dysenteriae', 'P. mirabilis'
    ]
}

def create_model() -> BacteriaClassifier:
    """Создает и возвращает модель с предустановленной таксономией"""
    return BacteriaClassifier(
        num_families=len(BACTERIA_TAXONOMY['families']),
        num_genera=len(BACTERIA_TAXONOMY['genera']),
        num_species=len(BACTERIA_TAXONOMY['species'])
    )

def load_model_checkpoint(model: BacteriaClassifier, checkpoint_path: str) -> BacteriaClassifier:
    """Загружает веса модели из чекпоинта"""
    try:
        checkpoint = torch.load(checkpoint_path, map_location='cpu')
        model.load_state_dict(checkpoint['model_state_dict'])
        print(f"Модель загружена из {checkpoint_path}")
    except FileNotFoundError:
        print(f"Чекпоинт не найден: {checkpoint_path}")
    except Exception as e:
        print(f"Ошибка при загрузке модели: {e}")
    
    return model
