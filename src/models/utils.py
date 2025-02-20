"""
Fonctions utilitaires pour les modèles de prédiction.
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import ta
from typing import Dict, List, Tuple, Union
import logging
from .config import DATA_CONFIG, TECHNICAL_INDICATORS, LOGGING_CONFIG

# Configuration du logging
logging.basicConfig(**LOGGING_CONFIG)
logger = logging.getLogger(__name__)

def prepare_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prépare les données pour l'entraînement en ajoutant les indicateurs techniques.
    
    Args:
        df (pd.DataFrame): DataFrame avec les données brutes
        
    Returns:
        pd.DataFrame: DataFrame avec les indicateurs techniques ajoutés
    """
    try:
        df = df.copy()
        
        # Ajout RSI
        if 'RSI' in TECHNICAL_INDICATORS:
            df['RSI'] = ta.momentum.RSIIndicator(
                close=df['close_price'], 
                window=TECHNICAL_INDICATORS['RSI']['period']
            ).rsi()
            
        # Ajout MACD
        if 'MACD' in TECHNICAL_INDICATORS:
            macd = ta.trend.MACD(
                close=df['close_price'],
                window_fast=TECHNICAL_INDICATORS['MACD']['fast_period'],
                window_slow=TECHNICAL_INDICATORS['MACD']['slow_period'],
                window_sign=TECHNICAL_INDICATORS['MACD']['signal_period']
            )
            df['MACD'] = macd.macd()
            df['MACD_signal'] = macd.macd_signal()
            df['MACD_diff'] = macd.macd_diff()
            
        # Ajout Bollinger Bands
        if 'BB' in TECHNICAL_INDICATORS:
            bb = ta.volatility.BollingerBands(
                close=df['close_price'],
                window=TECHNICAL_INDICATORS['BB']['period'],
                window_dev=TECHNICAL_INDICATORS['BB']['std_dev']
            )
            df['BB_high'] = bb.bollinger_hband()
            df['BB_low'] = bb.bollinger_lband()
            df['BB_mid'] = bb.bollinger_mavg()
            
        # Ajout EMA
        if 'EMA' in TECHNICAL_INDICATORS:
            for period in TECHNICAL_INDICATORS['EMA']['periods']:
                df[f'EMA_{period}'] = ta.trend.EMAIndicator(
                    close=df['close_price'],
                    window=period
                ).ema_indicator()
        
        # Suppression des lignes avec des NaN
        df = df.dropna()
        
        return df
        
    except Exception as e:
        logger.error(f"Erreur lors de la préparation des données: {str(e)}")
        raise

def create_sequences(data: np.ndarray, seq_length: int) -> Tuple[np.ndarray, np.ndarray]:
    """
    Crée des séquences pour l'entraînement des modèles de type séquence (LSTM).
    
    Args:
        data (np.ndarray): Données d'entrée
        seq_length (int): Longueur de la séquence
        
    Returns:
        Tuple[np.ndarray, np.ndarray]: Séquences X et y
    """
    X, y = [], []
    for i in range(len(data) - seq_length):
        X.append(data[i:(i + seq_length)])
        y.append(data[i + seq_length])
    return np.array(X), np.array(y)

def evaluate_predictions(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    """
    Évalue les prédictions en utilisant plusieurs métriques.
    
    Args:
        y_true (np.ndarray): Valeurs réelles
        y_pred (np.ndarray): Valeurs prédites
        
    Returns:
        Dict[str, float]: Dictionnaire des métriques
    """
    try:
        metrics = {
            'RMSE': np.sqrt(mean_squared_error(y_true, y_pred)),
            'MAE': mean_absolute_error(y_true, y_pred),
            'MAPE': np.mean(np.abs((y_true - y_pred) / y_true)) * 100,
            'R2': r2_score(y_true, y_pred)
        }
        return metrics
    except Exception as e:
        logger.error(f"Erreur lors de l'évaluation des prédictions: {str(e)}")
        raise

def split_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Divise les données en ensembles d'entraînement, validation et test.
    
    Args:
        df (pd.DataFrame): DataFrame complet
        
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]: Train, validation et test sets
    """
    try:
        n = len(df)
        train_size = int(n * DATA_CONFIG['TRAIN_TEST_SPLIT'])
        val_size = int(train_size * DATA_CONFIG['VALIDATION_SPLIT'])
        
        train = df[:train_size-val_size]
        val = df[train_size-val_size:train_size]
        test = df[train_size:]
        
        return train, val, test
    except Exception as e:
        logger.error(f"Erreur lors de la division des données: {str(e)}")
        raise 