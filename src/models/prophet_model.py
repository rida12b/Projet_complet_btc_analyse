"""
Module d'implémentation du modèle Prophet pour la prédiction du Bitcoin.
"""
import logging
import os
import pickle
from datetime import datetime
import pandas as pd
import numpy as np
from prophet import Prophet
from src.models.config import (
    PROPHET_CONFIG,
    MODEL_PATHS,
    LOGGING_CONFIG,
    TECHNICAL_INDICATORS
)
from src.models.features import calculate_technical_indicators, prepare_prophet_data
import ta

# Configuration du logging
os.makedirs(os.path.dirname(LOGGING_CONFIG['filename']), exist_ok=True)
logging.basicConfig(**LOGGING_CONFIG)
logger = logging.getLogger(__name__)

class BitcoinProphetModel:
    """Modèle Prophet pour la prédiction du prix du Bitcoin."""
    
    def __init__(self):
        """Initialise le modèle Prophet avec les paramètres optimisés."""
        self.model = Prophet(
            changepoint_prior_scale=0.1,
            seasonality_prior_scale=20.0,
            holidays_prior_scale=10.0,
            daily_seasonality=True,
            weekly_seasonality=True,
            yearly_seasonality=True,
            changepoint_range=0.95,
            n_changepoints=35,
            interval_width=0.95
        )
        
        # Ajout des régresseurs
        for col in ['ema_5', 'ema_8', 'ema_13', 'ema_21', 'momentum', 'volume_norm',
                   'trend_1d', 'trend_3d', 'trend_5d']:  # Ajout des tendances
            self.model.add_regressor(col, mode='multiplicative', standardize=True)
            
        # Ajout d'une saisonnalité mensuelle personnalisée
        self.model.add_seasonality(
            name='monthly',
            period=30.5,
            fourier_order=10,
            mode='multiplicative'
        )
        
        self.last_data = None
        self.is_trained = False
    
    def prepare_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prépare les données pour le modèle Prophet."""
        # Copie pour éviter de modifier les données originales
        df = df.copy()
        
        # Conversion des timestamps et tri
        df['ds'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('ds')
        
        # Normalisation du prix (log transformation)
        df['y'] = np.log1p(df['close_price'])
        
        # Calcul des indicateurs techniques
        df['ema_5'] = df['close_price'].ewm(span=5, adjust=False).mean()
        df['ema_8'] = df['close_price'].ewm(span=8, adjust=False).mean()
        df['ema_13'] = df['close_price'].ewm(span=13, adjust=False).mean()
        df['ema_21'] = df['close_price'].ewm(span=21, adjust=False).mean()
        
        # Normalisation des EMAs
        for col in ['ema_5', 'ema_8', 'ema_13', 'ema_21']:
            df[col] = np.log1p(df[col])
        
        # Calcul du momentum et des tendances
        df['momentum'] = df['close_price'].pct_change()
        df['trend_1d'] = df['close_price'].diff()
        df['trend_3d'] = df['close_price'].diff(3)
        df['trend_5d'] = df['close_price'].diff(5)
        
        # Normalisation des tendances
        for col in ['trend_1d', 'trend_3d', 'trend_5d']:
            df[col] = df[col] / df['close_price'].shift(1)
            
        # Normalisation du volume
        df['volume_norm'] = np.log1p(df['volume'])
        
        # Features temporelles
        df['year'] = df['ds'].dt.year
        df['month'] = df['ds'].dt.month
        df['day_of_week'] = df['ds'].dt.dayofweek
        df['day_of_month'] = df['ds'].dt.day
        df['week_of_year'] = df['ds'].dt.isocalendar().week
        
        # Gestion des NaN
        df = df.fillna(method='ffill').fillna(method='bfill')
        
        return df

    def train(self, data: pd.DataFrame):
        """Entraîne le modèle Prophet."""
        df = self.prepare_data(data)
        
        # Entraîner le modèle
        self.model.fit(df)
        self.last_data = df
        self.is_trained = True
        
        # Sauvegarder automatiquement le modèle
        self.save()
    
    def predict(self, data: pd.DataFrame, horizon: int) -> pd.DataFrame:
        """
        Fait des prédictions pour un nombre donné de jours.
        
        Args:
            data: DataFrame avec les données historiques
            horizon: Nombre de jours à prédire
            
        Returns:
            DataFrame avec les prédictions
        """
        if not self.is_trained:
            self.train(data)
        
        # Préparer les données
        prepared_data = self.prepare_data(data)
        
        # Création des dates futures
        last_date = prepared_data['ds'].max()
        future_dates = pd.date_range(start=last_date, periods=horizon + 1)[1:]
        future = pd.DataFrame({'ds': future_dates})
        
        # Calcul des indicateurs techniques pour les dates futures
        # On utilise les dernières valeurs connues pour les régresseurs
        for col in ['ema_5', 'ema_8', 'ema_13', 'ema_21']:
            future[col] = prepared_data[col].iloc[-1]
            
        future['momentum'] = prepared_data['momentum'].iloc[-1]
        future['trend_1d'] = prepared_data['trend_1d'].iloc[-1]
        future['trend_3d'] = prepared_data['trend_3d'].iloc[-1]
        future['trend_5d'] = prepared_data['trend_5d'].iloc[-1]
        future['volume_norm'] = prepared_data['volume_norm'].mean()
        
        # Faire la prédiction
        forecast = self.model.predict(future)
        
        return forecast
    
    def save(self, model_path: str = None):
        """
        Sauvegarde le modèle avec pickle.
        
        Args:
            model_path: Chemin de sauvegarde (optionnel)
        """
        try:
            if model_path is None:
                model_path = MODEL_PATHS['PROPHET']
            
            os.makedirs(os.path.dirname(model_path), exist_ok=True)
            
            # Créer un dictionnaire avec l'état du modèle
            state = {
                'model': self.model,
                'last_data': self.last_data.copy() if self.last_data is not None else None,
                'is_trained': self.is_trained
            }
            
            with open(model_path, 'wb') as f:
                pickle.dump(state, f)
                
            logger.info(f"Modèle sauvegardé avec succès dans {model_path}")
            
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde du modèle : {str(e)}")
            raise
    
    @staticmethod
    def load(model_path: str = None):
        """
        Charge un modèle sauvegardé.
        
        Args:
            model_path: Chemin vers le modèle sauvegardé
        
        Returns:
            BitcoinProphetModel: Instance du modèle chargé
        """
        try:
            if model_path is None:
                model_path = MODEL_PATHS['PROPHET']
            
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"Aucun modèle trouvé à {model_path}")
            
            with open(model_path, 'rb') as f:
                state = pickle.load(f)
            
            # Créer une nouvelle instance
            model = BitcoinProphetModel()
            
            # Restaurer l'état
            model.model = state['model']
            model.last_data = state['last_data']
            model.is_trained = state['is_trained']
            
            logger.info(f"Modèle chargé avec succès depuis {model_path}")
            return model
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement du modèle : {str(e)}")
            raise 