"""
Classe de base abstraite pour les modèles de prédiction.
"""

from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
import logging
from .config import LOGGING_CONFIG
from .utils import evaluate_predictions

# Configuration du logging
logging.basicConfig(**LOGGING_CONFIG)
logger = logging.getLogger(__name__)

class BaseModel(ABC):
    """Classe de base abstraite pour tous les modèles de prédiction."""
    
    def __init__(self, name: str):
        """
        Initialise le modèle.
        
        Args:
            name (str): Nom du modèle
        """
        self.name = name
        self.model = None
        self.is_fitted = False
        
    @abstractmethod
    def preprocess(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Prétraite les données pour le modèle.
        
        Args:
            data (pd.DataFrame): Données brutes
            
        Returns:
            pd.DataFrame: Données prétraitées
        """
        pass
    
    @abstractmethod
    def fit(self, train_data: pd.DataFrame, val_data: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
        """
        Entraîne le modèle sur les données.
        
        Args:
            train_data (pd.DataFrame): Données d'entraînement
            val_data (Optional[pd.DataFrame]): Données de validation
            
        Returns:
            Dict[str, Any]: Métriques d'entraînement
        """
        pass
    
    @abstractmethod
    def predict(self, data: pd.DataFrame) -> np.ndarray:
        """
        Fait des prédictions sur les données.
        
        Args:
            data (pd.DataFrame): Données pour la prédiction
            
        Returns:
            np.ndarray: Prédictions
        """
        pass
    
    def evaluate(self, test_data: pd.DataFrame, predictions: np.ndarray) -> Dict[str, float]:
        """
        Évalue les performances du modèle.
        
        Args:
            test_data (pd.DataFrame): Données de test
            predictions (np.ndarray): Prédictions du modèle
            
        Returns:
            Dict[str, float]: Métriques d'évaluation
        """
        try:
            y_true = test_data[self.target_column].values
            metrics = evaluate_predictions(y_true, predictions)
            logger.info(f"Évaluation du modèle {self.name}:")
            for metric, value in metrics.items():
                logger.info(f"{metric}: {value:.4f}")
            return metrics
        except Exception as e:
            logger.error(f"Erreur lors de l'évaluation du modèle {self.name}: {str(e)}")
            raise
    
    @abstractmethod
    def save(self, path: str):
        """
        Sauvegarde le modèle.
        
        Args:
            path (str): Chemin de sauvegarde
        """
        pass
    
    @abstractmethod
    def load(self, path: str):
        """
        Charge le modèle.
        
        Args:
            path (str): Chemin du modèle à charger
        """
        pass 