"""
Module de calcul des indicateurs techniques pour le Bitcoin.
"""
import pandas as pd
import numpy as np
import ta
from src.models.config import TECHNICAL_INDICATORS

def calculate_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcule les indicateurs techniques pour les données Bitcoin.
    
    Args:
        df: DataFrame avec colonnes OHLCV (timestamp, open, high, low, close, volume)
    
    Returns:
        DataFrame avec indicateurs techniques ajoutés
    """
    # Copie pour ne pas modifier l'original
    df = df.copy()
    
    # RSI
    if 'RSI' in TECHNICAL_INDICATORS:
        df['rsi'] = ta.momentum.RSIIndicator(
            close=df['close_price'],
            window=TECHNICAL_INDICATORS['RSI']['period']
        ).rsi()
    
    # MACD
    if 'MACD' in TECHNICAL_INDICATORS:
        macd = ta.trend.MACD(
            close=df['close_price'],
            window_fast=TECHNICAL_INDICATORS['MACD']['fast_period'],
            window_slow=TECHNICAL_INDICATORS['MACD']['slow_period'],
            window_sign=TECHNICAL_INDICATORS['MACD']['signal_period']
        )
        df['macd'] = macd.macd()
        df['macd_signal'] = macd.macd_signal()
        df['macd_diff'] = macd.macd_diff()
    
    # Bollinger Bands
    if 'BB' in TECHNICAL_INDICATORS:
        bollinger = ta.volatility.BollingerBands(
            close=df['close_price'],
            window=TECHNICAL_INDICATORS['BB']['period'],
            window_dev=TECHNICAL_INDICATORS['BB']['std_dev']
        )
        df['bb_high'] = bollinger.bollinger_hband()
        df['bb_mid'] = bollinger.bollinger_mavg()
        df['bb_low'] = bollinger.bollinger_lband()
    
    # EMA
    if 'EMA' in TECHNICAL_INDICATORS:
        for period in TECHNICAL_INDICATORS['EMA']['periods']:
            df[f'ema_{period}'] = ta.trend.EMAIndicator(
                close=df['close_price'],
                window=period
            ).ema_indicator()
    
    # Volatilité
    df['volatility'] = df['close_price'].pct_change().rolling(window=30).std()
    
    # Volume moyen
    df['volume_sma'] = df['volume'].rolling(window=20).mean()
    
    # Retours sur différentes périodes
    for period in [1, 7, 14, 30]:
        df[f'return_{period}d'] = df['close_price'].pct_change(periods=period)
    
    # Gestion des valeurs NaN
    # Pour les indicateurs techniques, on remplace par la moyenne
    technical_columns = ['rsi', 'macd', 'macd_signal', 'macd_diff', 
                        'bb_high', 'bb_mid', 'bb_low', 'volatility', 'volume_sma']
    technical_columns.extend([f'ema_{p}' for p in TECHNICAL_INDICATORS['EMA']['periods']])
    
    for col in technical_columns:
        if col in df.columns:
            df[col] = df[col].fillna(df[col].mean())
    
    # Pour les retours, on remplace par 0
    return_columns = [f'return_{p}d' for p in [1, 7, 14, 30]]
    for col in return_columns:
        if col in df.columns:
            df[col] = df[col].fillna(0)
    
    return df

def prepare_prophet_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prépare les données pour Prophet.
    
    Args:
        df: DataFrame avec les données Bitcoin
    
    Returns:
        DataFrame au format Prophet (ds, y)
    """
    prophet_df = pd.DataFrame()
    prophet_df['ds'] = pd.to_datetime(df['timestamp'])
    prophet_df['y'] = df['close_price']
    
    # Ajout des régresseurs (indicateurs techniques)
    for col in df.columns:
        if col not in ['timestamp', 'close_price']:
            prophet_df[col] = df[col]
    
    return prophet_df 