"""
Configuration des modèles d'IA pour la prédiction du Bitcoin.
Contient les paramètres de configuration pour Prophet et LSTM.
"""

# Configuration générale des données
DATA_CONFIG = {
    'TRAIN_TEST_SPLIT': 0.8,  # 80% pour l'entraînement, 20% pour le test
    'VALIDATION_SPLIT': 0.1,  # 10% des données d'entraînement pour la validation
    'SEQUENCE_LENGTH': 60,  # Nombre de points de données historiques à utiliser
    'PREDICTION_HORIZON': 7,  # Nombre de points à prédire dans le futur
    'TARGET_COLUMN': 'close',  # Colonne cible pour la prédiction
}

# Configuration de Prophet
PROPHET_CONFIG = {
    'changepoint_prior_scale': 0.05,     # Augmenté pour plus de flexibilité
    'seasonality_prior_scale': 10.0,     # Augmenté pour donner plus d'importance aux saisonnalités
    'holidays_prior_scale': 10.0,        # Augmenté pour les effets des jours fériés
    'seasonality_mode': 'multiplicative', # Meilleur pour les données financières
    'daily_seasonality': True,           # Activé explicitement
    'weekly_seasonality': True,          # Déjà activé par défaut
    'yearly_seasonality': True,          # Activé explicitement
    'interval_width': 0.95,
    'changepoint_range': 0.9,            # Augmenté pour capturer plus de changements
    'n_changepoints': 25,                # Augmenté pour plus de flexibilité
    'growth': 'linear'
}

# Configuration des indicateurs techniques
TECHNICAL_INDICATORS = {
    'RSI': {'period': 14},
    'MACD': {'fast_period': 12, 'slow_period': 26, 'signal_period': 9},
    'BB': {'period': 20, 'std_dev': 2},
    'EMA': {'periods': [9, 21, 50, 200]},
}

# Métriques d'évaluation
METRICS = [
    'RMSE',  # Root Mean Square Error
    'MAE',   # Mean Absolute Error
    'MAPE',  # Mean Absolute Percentage Error
    'R2'     # Coefficient de détermination
]

# Chemins des fichiers
MODEL_PATHS = {
    'PROPHET': 'models/prophet_model.pkl',
    'LSTM': 'models/lstm_model.h5',
    'SCALER': 'models/scaler.pkl',
}

# Configuration des logs
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'filename': 'logs/model_training.log'
}

# Paramètres de visualisation
VISUALIZATION_CONFIG = {
    'figsize': (15, 8),
    'style': 'seaborn',
    'prediction_color': '#2ecc71',
    'actual_color': '#3498db',
    'confidence_interval_color': 'rgba(46, 204, 113, 0.2)'
} 