"""
Tests du collecteur de données Bitcoin.
"""
import pytest
import sqlite3
import os
from datetime import datetime
from unittest.mock import patch, MagicMock

from src.data.collector import BitcoinDataCollector
from src.data import config as data_config

@pytest.fixture
def test_db():
    """Fixture pour créer une base de données de test."""
    test_db_file = "test_bitcoin_trends.db"
    
    # Supprimer la base de test si elle existe
    if os.path.exists(test_db_file):
        os.remove(test_db_file)
    
    # Créer la connexion et la table
    conn = sqlite3.connect(test_db_file)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE bitcoin_prices (
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
    """)
    
    conn.commit()
    conn.close()
    
    return test_db_file

@pytest.fixture
def collector(test_db):
    """Fixture pour créer un collecteur avec une base de test."""
    # Sauvegarder le chemin original
    original_db = data_config.DB_FILE
    
    # Utiliser la base de test
    data_config.DB_FILE = test_db
    
    collector = BitcoinDataCollector()
    collector.connect_db()
    yield collector
    
    # Fermer les connexions
    if collector.db_cursor:
        collector.db_cursor.close()
    if collector.db_conn:
        collector.db_conn.close()
    
    # Restaurer le chemin original
    data_config.DB_FILE = original_db

def test_api_connection(collector):
    """Test de la connexion à l'API Coinalyze."""
    mock_response = MagicMock()
    mock_response.json.return_value = [{
        "t": int(datetime.now().timestamp()),
        "o": 50000.0,
        "h": 51000.0,
        "l": 49000.0,
        "c": 50500.0,
        "v": 1000.0,
        "vb": 500.0,
        "n": 1000,
        "nb": 500
    }]
    
    with patch('requests.Session.get', return_value=mock_response):
        price_data = collector.fetch_current_price()
        assert price_data is not None
        assert len(price_data) == 9  # timestamp + 8 champs de données
        
        # Vérification des types de données
        assert isinstance(price_data[0], str)  # timestamp en str pour SQLite
        assert all(isinstance(x, (float, int)) for x in price_data[1:])

def test_database_connection(collector):
    """Test de la connexion à la base de données."""
    assert collector.db_conn is not None
    assert collector.db_cursor is not None
    
    # Vérifier que la table existe
    collector.db_cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name='bitcoin_prices';
    """)
    assert collector.db_cursor.fetchone() is not None

def test_data_collection(collector):
    """Test de la collecte et sauvegarde des données."""
    mock_response = MagicMock()
    mock_response.json.return_value = [{
        "t": int(datetime.now().timestamp()),
        "o": 50000.0,
        "h": 51000.0,
        "l": 49000.0,
        "c": 50500.0,
        "v": 1000.0,
        "vb": 500.0,
        "n": 1000,
        "nb": 500
    }]
    
    with patch('requests.Session.get', return_value=mock_response):
        # Collecte des données
        collector.collect_data()
        
        # Vérification que les données ont été sauvegardées
        collector.db_cursor.execute("SELECT COUNT(*) FROM bitcoin_prices;")
        count = collector.db_cursor.fetchone()[0]
        assert count > 0, "Aucune donnée n'a été sauvegardée"
        
        # Récupération de la dernière entrée
        collector.db_cursor.execute("""
            SELECT * FROM bitcoin_prices
            ORDER BY timestamp DESC
            LIMIT 1;
        """)
        last_record = collector.db_cursor.fetchone()
        assert last_record is not None, "Impossible de récupérer la dernière entrée"
        
        print("\nDernière entrée dans la base de données:")
        print(f"ID: {last_record[0]}")
        print(f"Timestamp: {last_record[1]}")
        print(f"Open: {last_record[2]}")
        print(f"High: {last_record[3]}")
        print(f"Low: {last_record[4]}")
        print(f"Close: {last_record[5]}")
        print(f"Volume: {last_record[6]}")
        print(f"Volume Buy: {last_record[7]}")
        print(f"Trades: {last_record[8]}")
        print(f"Trades Buy: {last_record[9]}") 