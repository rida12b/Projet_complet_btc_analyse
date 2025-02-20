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
COINALYZE_API_KEY = os.getenv("COINALYZE_API_KEY")
DEFAULT_SYMBOL = "BTCUSDC.A"  # BTC/USDC sur Binance
DEFAULT_INTERVAL = "1hour"     # Intervalle horaire
DEFAULT_EXCHANGE = "binance"  # Exchange par défaut

# Configuration de la collecte
# Calcul de la date de début (3 mois avant aujourd'hui)
DEFAULT_START_DATE = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
UPDATE_INTERVAL = 3600  # Mise à jour toutes les heures
RATE_LIMIT_WAIT = 10   # Attente de 10 secondes entre les requêtes

# Configuration de la base de données SQLite
DB_FILE = "data/bitcoin_trends.db"

# Configuration du logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = "logs/data_collection.log"

# Schéma de la base de données
PRICE_TABLE_SCHEMA = """
CREATE TABLE IF NOT EXISTS bitcoin_prices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TIMESTAMP NOT NULL,
    open_price REAL NOT NULL,
    high_price REAL NOT NULL,
    low_price REAL NOT NULL,
    close_price REAL NOT NULL,
    volume REAL,
    volume_buy REAL,
    transactions INTEGER,
    transactions_buy INTEGER,
    UNIQUE(timestamp)
);
"""

# Index pour les performances
PRICE_TABLE_INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_bitcoin_prices_timestamp ON bitcoin_prices(timestamp);"
]

# Configuration du cache
CACHE_DURATION = 3600  # Durée de cache en secondes (1 heure) 