"""
Tests pour le collecteur de données Bitcoin.
"""
import pytest
from datetime import datetime, timezone
from src.data.collector import BitcoinDataCollector

@pytest.fixture
def collector():
    """Fixture pour créer une instance du collecteur."""
    return BitcoinDataCollector()

def test_api_connection(collector):
    """Test de la connexion à l'API Coinalyze."""
    try:
        price_data = collector.fetch_current_price()
        assert price_data is not None
        assert len(price_data) == 9  # timestamp + 8 champs de données
        
        # Vérification des types de données
        assert isinstance(price_data[0], str)  # timestamp en str pour SQLite
        assert all(isinstance(x, (float, int)) for x in price_data[1:])
        
    except Exception as e:
        pytest.fail(f"Erreur lors de la connexion à l'API: {str(e)}")

def test_database_connection(collector):
    """Test de la connexion à la base de données."""
    try:
        collector.connect_db()
        assert collector.db_conn is not None
        assert collector.db_cursor is not None
        
        # Vérification que la table existe
        collector.db_cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='bitcoin_prices';
        """)
        table_exists = collector.db_cursor.fetchone() is not None
        assert table_exists, "La table bitcoin_prices n'existe pas"
        
        # Vérification de la structure de la table
        collector.db_cursor.execute("PRAGMA table_info(bitcoin_prices);")
        columns = collector.db_cursor.fetchall()
        
        expected_columns = [
            (0, 'id', 'INTEGER', 0, None, 1),
            (1, 'timestamp', 'TIMESTAMP', 1, None, 0),
            (2, 'open_price', 'REAL', 1, None, 0),
            (3, 'high_price', 'REAL', 1, None, 0),
            (4, 'low_price', 'REAL', 1, None, 0),
            (5, 'close_price', 'REAL', 1, None, 0),
            (6, 'volume', 'REAL', 1, None, 0),
            (7, 'volume_buy', 'REAL', 1, None, 0),
            (8, 'transactions', 'INTEGER', 1, None, 0),
            (9, 'transactions_buy', 'INTEGER', 1, None, 0)
        ]
        
        assert len(columns) == len(expected_columns), "Nombre incorrect de colonnes"
        for col, exp_col in zip(columns, expected_columns):
            assert col[1] == exp_col[1], f"Nom de colonne incorrect: {col[1]} != {exp_col[1]}"
            assert col[2] == exp_col[2], f"Type de colonne incorrect pour {col[1]}"
        
    except Exception as e:
        pytest.fail(f"Erreur lors de la connexion à la base de données: {str(e)}")
    finally:
        collector.close()

def test_data_collection(collector):
    """Test de la collecte et sauvegarde des données."""
    try:
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
        
    except Exception as e:
        pytest.fail(f"Erreur lors de la collecte des données: {str(e)}")
    finally:
        collector.close() 