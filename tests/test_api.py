"""
Tests des endpoints de l'API REST Bitcoin Trends.
"""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import sqlite3
import os
from unittest.mock import patch, MagicMock
import pandas as pd
import numpy as np

from src.api.main import app, get_prophet_model
from src.data.collector import BitcoinDataCollector
from src.models.prophet_model import BitcoinProphetModel
from src.models.config import MODEL_PATHS
from src.data import config as data_config

@pytest.fixture(scope="session")
def session_db():
    """Fixture pour créer une base de données de test pour toute la session."""
    # Utiliser une base de données temporaire pour les tests
    test_db_file = "test_bitcoin_trends.db"
    
    # Supprimer la base de test si elle existe
    if os.path.exists(test_db_file):
        os.remove(test_db_file)
    
    # Créer la connexion et la table
    conn = sqlite3.connect(test_db_file)
    cursor = conn.cursor()
    
    # Créer la table avec le même schéma
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
    
    # Générer 30 jours de données de test
    test_data = []
    base_price = 50000.0
    base_volume = 1000.0
    base_transactions = 1000
    
    for i in range(30):
        current_date = datetime.now() - timedelta(days=29-i)
        # Simuler une tendance haussière légère
        daily_change = (i / 30) * 1000  # Augmentation progressive sur 30 jours
        current_price = base_price + daily_change
        
        # Ajouter des variations quotidiennes
        open_price = current_price * (1 + (i % 2) * 0.01)
        high_price = current_price * 1.02
        low_price = current_price * 0.98
        close_price = current_price * (1 - (i % 2) * 0.01)
        
        # Variations du volume
        volume = base_volume * (1 + (i % 3) * 0.1)
        volume_buy = volume * 0.6
        
        # Variations des transactions
        transactions = base_transactions * (1 + (i % 3) * 0.1)
        transactions_buy = int(transactions * 0.6)
        
        test_data.append((
            current_date.strftime('%Y-%m-%d %H:%M:%S'),
            open_price,
            high_price,
            low_price,
            close_price,
            volume,
            volume_buy,
            transactions,
            transactions_buy
        ))
    
    cursor.executemany("""
        INSERT INTO bitcoin_prices (
            timestamp, open_price, high_price, low_price,
            close_price, volume, volume_buy, transactions, transactions_buy
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, test_data)
    
    conn.commit()
    conn.close()
    
    # Retourner le chemin de la base de test
    return test_db_file

@pytest.fixture(scope="session")
def trained_model(session_db):
    """Fixture pour entraîner et sauvegarder le modèle avant les tests."""
    # Utiliser la base de test
    data_config.DB_FILE = session_db
    
    # Créer et entraîner le modèle
    model = BitcoinProphetModel()
    
    # Charger les données
    conn = sqlite3.connect(session_db)
    df = pd.read_sql_query("""
        SELECT timestamp, open_price, high_price, low_price, close_price, volume
        FROM bitcoin_prices
        ORDER BY timestamp ASC;
    """, conn)
    conn.close()
    
    # Entraîner le modèle
    model.train(df)
    
    # Sauvegarder le modèle
    os.makedirs(os.path.dirname(MODEL_PATHS["PROPHET"]), exist_ok=True)
    model.save(MODEL_PATHS["PROPHET"])
    
    return model

@pytest.fixture
def client(mock_model):
    """Fixture pour créer un client de test."""
    app.dependency_overrides[get_prophet_model] = lambda: mock_model
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

@pytest.fixture
def sample_data(session_db):
    """Fixture pour insérer des données de test."""
    # Sauvegarder le chemin original
    original_db = data_config.DB_FILE
    
    # Utiliser la base de test
    data_config.DB_FILE = session_db
    
    yield
    
    # Restaurer le chemin original
    data_config.DB_FILE = original_db

@pytest.fixture
def mock_model():
    """Fixture pour mocker le modèle Prophet."""
    mock_model = MagicMock()
    
    # Configuration du mock pour predict
    def mock_predict(df, horizon):
        dates = pd.date_range(start=datetime.now(), periods=horizon, freq='D')
        return pd.DataFrame({
            'ds': dates,
            'yhat': np.log1p(np.random.normal(50000, 1000, horizon)),
            'yhat_lower': np.log1p(np.random.normal(48000, 1000, horizon)),
            'yhat_upper': np.log1p(np.random.normal(52000, 1000, horizon)),
            'trend': np.random.normal(10, 0.1, horizon),
            'weekly': np.random.normal(0, 0.1, horizon),
            'yearly': np.random.normal(0, 0.1, horizon)
        })
    
    mock_model.predict.side_effect = mock_predict
    mock_model.is_trained = True
    mock_model.load.return_value = None
    
    return mock_model

def test_root(client):
    """Test de la page d'accueil."""
    response = client.get("/")
    assert response.status_code == 200
    assert "name" in response.json()
    assert "version" in response.json()

def test_get_latest_price(client, sample_data):
    """Test de récupération du dernier prix."""
    response = client.get("/api/v1/prices/latest")
    assert response.status_code == 200
    data = response.json()
    assert "timestamp" in data
    assert "close_price" in data
    assert "volume" in data

def test_get_historical_prices(client, sample_data):
    """Test de récupération des prix historiques."""
    # Test avec paramètres par défaut
    response = client.get("/api/v1/prices/historical")
    assert response.status_code == 200
    data = response.json()
    assert len(data) <= 100  # Limite par défaut
    
    # Test avec période spécifique
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    response = client.get(
        f"/api/v1/prices/historical?start_date={start_date}&end_date={end_date}&limit=50"
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) <= 50

def test_get_price_stats(client, sample_data):
    """Test de récupération des statistiques."""
    # Test pour différentes périodes
    for period in ["24h", "7d", "30d"]:
        response = client.get(f"/api/v1/prices/stats?period={period}")
        assert response.status_code == 200
        data = response.json()
        assert "min_price" in data
        assert "max_price" in data
        assert "avg_price" in data
        assert data["period"] == period

def test_predict_prices(client, mock_model):
    """Test des prédictions de prix."""
    # Test de prédiction simple
    request_data = {"horizon": 7, "return_components": False}
    response = client.post("/api/v1/predict", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert "dates" in data
    assert "predictions" in data
    assert "lower_bounds" in data
    assert "upper_bounds" in data
    assert len(data["dates"]) == 7
    assert len(data["predictions"]) == 7
    assert len(data["lower_bounds"]) == 7
    assert len(data["upper_bounds"]) == 7
    
    # Test avec composantes
    request_data = {"horizon": 5, "return_components": True}
    response = client.post("/api/v1/predict", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert "components" in data
    assert "trend" in data["components"]
    assert len(data["dates"]) == 5

def test_model_info(client):
    """Test des informations du modèle."""
    response = client.get("/api/v1/model/info")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Prophet"
    assert "version" in data
    assert "parameters" in data
    assert "metrics" in data
    assert "last_training" in data
    assert "features" in data

def test_error_handling(client, mock_model):
    """Test de la gestion des erreurs."""
    # Test avec un horizon invalide
    request_data = {"horizon": -1}
    response = client.post("/api/v1/predict", json=request_data)
    assert response.status_code == 400
    assert "detail" in response.json()
    
    # Test avec un horizon trop grand
    request_data = {"horizon": 1000}
    response = client.post("/api/v1/predict", json=request_data)
    assert response.status_code == 400
    assert "detail" in response.json()

    # Test avec des dates invalides
    response = client.get("/api/v1/prices/historical?start_date=invalid")
    assert response.status_code == 400

    # Test avec une période invalide
    response = client.get("/api/v1/prices/stats?period=invalid")
    assert response.status_code == 400 