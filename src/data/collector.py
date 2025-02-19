"""
Script de collecte des données Bitcoin depuis Coinalyze.
"""
import logging
import os
import sqlite3
from datetime import datetime, timezone, timedelta
import requests
from src.data.config import (
    COINALYZE_BASE_URL,
    COINALYZE_API_KEY,
    DEFAULT_SYMBOL,
    DEFAULT_INTERVAL,
    DB_FILE,
    PRICE_TABLE_SCHEMA,
    PRICE_TABLE_INDEXES,
    LOG_LEVEL,
    LOG_FORMAT,
    LOG_FILE
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
        
    def fetch_current_price(self):
        """Récupère les dernières données Bitcoin."""
        try:
            # Calcul des timestamps pour les dernières 24h
            end_time = int(datetime.now(timezone.utc).timestamp())
            start_time = end_time - (60 * 60)  # Dernière heure seulement
            
            # Construction de l'URL avec les paramètres
            url = f"{COINALYZE_BASE_URL}/ohlcv-history"
            params = {
                "api_key": COINALYZE_API_KEY,
                "symbols": DEFAULT_SYMBOL,
                "interval": DEFAULT_INTERVAL,
                "from": start_time,
                "to": end_time
            }
            
            logging.info(f"Requête API : {url} avec params={params}")
            response = self.session.get(url, params=params)
            
            if response.status_code != 200:
                logging.error(f"Réponse API : {response.status_code} - {response.text}")
            response.raise_for_status()
            
            data = response.json()
            
            if not data or not isinstance(data, list) or len(data) == 0:
                raise ValueError("Aucune donnée reçue de Coinalyze")
                
            # Récupérer les données du premier symbole
            symbol_data = data[0]
            if not symbol_data.get("history"):
                raise ValueError(f"Aucun historique trouvé pour le symbole {DEFAULT_SYMBOL}")
                
            # Prendre la dernière entrée de l'historique
            latest_data = symbol_data["history"][-1]
            
            # Vérification et correction du timestamp
            timestamp = latest_data["t"]
            if len(str(timestamp)) == 10:  # Si le timestamp est en secondes
                timestamp = timestamp * 1000
            elif len(str(timestamp)) > 13:  # Si le timestamp est trop long
                timestamp = timestamp // (10 ** (len(str(timestamp)) - 13))
                
            price_data = (
                datetime.fromtimestamp(timestamp / 1000, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S'),
                float(latest_data["o"]),
                float(latest_data["h"]),
                float(latest_data["l"]),
                float(latest_data["c"]),
                float(latest_data["v"]),
                float(latest_data.get("bv", 0)),
                int(latest_data.get("tx", 0)),
                int(latest_data.get("btx", 0))
            )
            
            return price_data
            
        except Exception as e:
            logging.error(f"Erreur lors de la requête à Coinalyze: {str(e)}")
            raise
            
    def save_price_data(self, price_data):
        """Sauvegarde les données de prix dans la base de données."""
        try:
            sql = """
                INSERT INTO bitcoin_prices
                (timestamp, open_price, high_price, low_price, close_price,
                 volume, volume_buy, transactions, transactions_buy)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            self.db_cursor.execute(sql, price_data)
            self.db_conn.commit()
            logger.info("Données de prix sauvegardées avec succès")
            
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des données: {str(e)}")
            self.db_conn.rollback()
            raise
            
    def collect_data(self):
        """Collecte et sauvegarde les données actuelles."""
        try:
            if not self.db_conn:
                self.connect_db()
                
            price_data = self.fetch_current_price()
            self.save_price_data(price_data)
            
        except Exception as e:
            logger.error(f"Erreur lors de la collecte des données: {str(e)}")
            raise
            
    def close(self):
        """Ferme les connexions."""
        if self.db_cursor:
            self.db_cursor.close()
        if self.db_conn:
            self.db_conn.close()
        logger.info("Connexions fermées")

if __name__ == "__main__":
    collector = BitcoinDataCollector()
    try:
        collector.collect_data()
    finally:
        collector.close() 