"""
Configuration pour la collecte des données Bitcoin.
"""
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Chargement des variables d'environnement
load_dotenv()

# Configuration de l'API Coinalyze
COINALYZE_BASE_URL = "https://api.coinalyze.net/v1"
COINALYZE_API_KEY = os.getenv("COINALYZE_API_KEY", "91dfe868-019c-48a7-965d-ec8753acd2bf")

# Configuration de la collecte
DEFAULT_SYMBOL = "BTCUSDC.A"  # BTC/USDC sur Binance
DEFAULT_INTERVAL = "1min"  # Changé de "1hour" à "1min" pour plus de précision
DEFAULT_START_DATE = datetime.now() - timedelta(days=1)  # 1 jour de données par défaut
UPDATE_INTERVAL = 60  # Intervalle de mise à jour en secondes

# Configuration de la base de données SQLite
DB_FILE = "data/bitcoin_trends.db"  # Chemin relatif vers le fichier de base de données

# Configuration du logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = "logs/data_collection.log"

# Schéma de la base de données
PRICE_TABLE_NAME = "bitcoin_prices"
PRICE_TABLE_SCHEMA = """
CREATE TABLE IF NOT EXISTS bitcoin_prices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TIMESTAMP NOT NULL,
    open_price REAL NOT NULL,
    high_price REAL NOT NULL,
    low_price REAL NOT NULL,
    close_price REAL NOT NULL,
    volume REAL NOT NULL,
    volume_buy REAL NOT NULL,
    transactions INTEGER NOT NULL,
    transactions_buy INTEGER NOT NULL
);
"""

# Index pour les performances
PRICE_TABLE_INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_bitcoin_prices_timestamp ON bitcoin_prices(timestamp);"
] 