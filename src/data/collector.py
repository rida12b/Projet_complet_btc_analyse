"""
Script de collecte des données Bitcoin depuis Coinalyze.
"""
import logging
import os
import sqlite3
import time
from datetime import datetime, timezone, timedelta
import requests
from src.data.config import (
    COINALYZE_BASE_URL,
    COINALYZE_API_KEY,
    DEFAULT_SYMBOL,
    DEFAULT_INTERVAL,
    DEFAULT_START_DATE,
    RATE_LIMIT_WAIT,
    DB_FILE,
    PRICE_TABLE_SCHEMA,
    PRICE_TABLE_INDEXES,
    LOG_LEVEL,
    LOG_FORMAT,
    LOG_FILE,
    DEFAULT_EXCHANGE
)

# Configuration du logging
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
# Création du répertoire data s'il n'existe pas
os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)

logging.basicConfig(
    level=LOG_LEVEL,
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BitcoinDataCollector:
    """Classe pour la collecte des données Bitcoin."""
    
    def __init__(self):
        """Initialisation du collecteur."""
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json",
            "api-key": COINALYZE_API_KEY
        })
        self.db_conn = None
        self.db_cursor = None
        
    def connect_db(self):
        """Établit la connexion à la base de données SQLite."""
        try:
            self.db_conn = sqlite3.connect(DB_FILE)
            self.db_cursor = self.db_conn.cursor()
            
            # Création de la table si elle n'existe pas
            self.db_cursor.execute(PRICE_TABLE_SCHEMA)
            
            # Création des index
            for index_sql in PRICE_TABLE_INDEXES:
                self.db_cursor.execute(index_sql)
            
            self.db_conn.commit()
            logging.info("Connexion à la base de données établie avec succès")
            
        except Exception as e:
            logging.error(f"Erreur de connexion à la base de données: {str(e)}")
            raise

    def fetch_historical_data(self, start_date=DEFAULT_START_DATE, batch_size=3):
        """
        Récupère les données historiques depuis Coinalyze par lots.
        
        Args:
            start_date (str): Date de début au format YYYY-MM-DD
            batch_size (int): Nombre de jours par lot
        """
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            end_dt = datetime.now(timezone.utc)
            current_start = start_dt
            
            while current_start < end_dt:
                current_end = min(current_start + timedelta(days=batch_size), end_dt)
                
                # Construction de l'URL avec les paramètres exacts
                url = f"{COINALYZE_BASE_URL}/ohlcv-history"
                params = {
                    "api_key": COINALYZE_API_KEY,
                    "symbols": DEFAULT_SYMBOL,
                    "interval": DEFAULT_INTERVAL,
                    "from": int(current_start.timestamp()),
                    "to": int(current_end.timestamp())
                }
                
                logger.info(f"Récupération des données du {current_start.date()} au {current_end.date()}")
                
                try:
                    response = self.session.get(url, params=params)
                    
                    if response.status_code == 429:  # Rate limit
                        retry_after = float(response.headers.get('Retry-After', RATE_LIMIT_WAIT))
                        logger.warning(f"Rate limit atteint, attente de {retry_after} secondes")
                        time.sleep(retry_after)
                        continue
                        
                    response.raise_for_status()
                    data = response.json()
                    
                    if not data or not data[0].get("history"):
                        logger.warning(f"Aucune donnée reçue pour la période {current_start.date()} - {current_end.date()}")
                        current_start = current_end + timedelta(seconds=1)
                        time.sleep(5)  # Petite pause avant de continuer
                        continue
                    
                    # Préparation des données pour la base
                    price_data = []
                    for entry in data[0]["history"]:
                        timestamp = entry["t"]
                        if len(str(timestamp)) == 10:  # Si le timestamp est en secondes
                            timestamp = timestamp * 1000
                        
                        price_data.append((
                            datetime.fromtimestamp(timestamp / 1000, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S'),
                            float(entry["o"]),
                            float(entry["h"]),
                            float(entry["l"]),
                            float(entry["c"]),
                            float(entry["v"]),
                            float(entry.get("vb", 0)),
                            int(entry.get("n", 0)),
                            int(entry.get("nb", 0))
                        ))
                    
                    # Sauvegarde du lot
                    if price_data:
                        self.save_price_data(price_data)
                        logger.info(f"✅ {len(price_data)} entrées sauvegardées pour la période")
                    
                    # Attente entre chaque lot pour respecter le rate limit
                    time.sleep(RATE_LIMIT_WAIT)
                    
                except requests.exceptions.RequestException as e:
                    logger.error(f"❌ Erreur lors de la requête: {str(e)}")
                    time.sleep(RATE_LIMIT_WAIT * 2)  # Attente plus longue en cas d'erreur
                    continue
                
                # Passage au lot suivant
                current_start = current_end + timedelta(seconds=1)
            
            logger.info("✅ Collecte de l'historique terminée avec succès")
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la récupération des données historiques: {str(e)}")
            raise
            
    def save_price_data(self, price_data):
        """
        Sauvegarde les données de prix dans la base de données.
        
        Args:
            price_data (list): Liste de tuples contenant les données à sauvegarder
        """
        try:
            sql = """
                INSERT OR REPLACE INTO bitcoin_prices
                (timestamp, open_price, high_price, low_price, close_price,
                 volume, volume_buy, transactions, transactions_buy)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            self.db_cursor.executemany(sql, price_data)
            self.db_conn.commit()
            logger.info(f"Sauvegarde de {len(price_data)} entrées réussie")
            
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des données: {str(e)}")
            self.db_conn.rollback()
            raise
            
    def collect_full_history(self):
        """Collecte l'historique complet des données."""
        try:
            if not self.db_conn:
                self.connect_db()
                
            # Récupération des données historiques
            self.fetch_historical_data()
            
            logger.info("Collecte de l'historique complet terminée avec succès")
            
        except Exception as e:
            logger.error(f"Erreur lors de la collecte de l'historique: {str(e)}")
            raise
            
    def close(self):
        """Ferme les connexions."""
        if self.db_cursor:
            self.db_cursor.close()
        if self.db_conn:
            self.db_conn.close()
        logger.info("Connexions fermées")

    def fetch_current_price(self):
        """Récupère le prix actuel du Bitcoin."""
        try:
            url = f"{COINALYZE_BASE_URL}/futures/ohlcv/latest"
            params = {
                "symbol": DEFAULT_SYMBOL,
                "exchange": DEFAULT_EXCHANGE,
                "interval": DEFAULT_INTERVAL
            }
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if not data:
                logger.warning("Aucune donnée reçue de l'API")
                return None
                
            entry = data[0]  # Premier élément du tableau
            timestamp = entry["t"]
            if len(str(timestamp)) == 10:  # Si le timestamp est en secondes
                timestamp = timestamp * 1000
                
            price_data = (
                datetime.fromtimestamp(timestamp / 1000, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S'),
                float(entry["o"]),
                float(entry["h"]),
                float(entry["l"]),
                float(entry["c"]),
                float(entry["v"]),
                float(entry.get("vb", 0)),
                int(entry.get("n", 0)),
                int(entry.get("nb", 0))
            )
            
            return price_data
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du prix actuel: {str(e)}")
            raise
            
    def collect_data(self):
        """Collecte les données actuelles et les sauvegarde."""
        try:
            if not self.db_conn:
                self.connect_db()
                
            price_data = self.fetch_current_price()
            if price_data:
                self.save_price_data([price_data])
                logger.info("Données actuelles collectées et sauvegardées avec succès")
            
        except Exception as e:
            logger.error(f"Erreur lors de la collecte des données: {str(e)}")
            raise

if __name__ == "__main__":
    collector = BitcoinDataCollector()
    try:
        collector.collect_full_history()
    finally:
        collector.close() 