"""
Tests pour l'API REST Bitcoin Trends.
"""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta

from src.api.main import app
from src.data.collector import BitcoinDataCollector

@pytest.fixture
def client():
    """Fixture pour créer un client de test."""
    return TestClient(app)

@pytest.fixture
def sample_data():
    """Fixture pour insérer des données de test."""
    collector = BitcoinDataCollector()
    try:
        collector.connect_db()
        collector.collect_data()  # Collecte des données réelles pour les tests
    finally:
        collector.close()

def test_root_endpoint(client):
    """Test de la page d'accueil de l'API."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data
    assert "description" in data

def test_latest_price(client, sample_data):
    """Test de la récupération du dernier prix."""
    response = client.get("/api/v1/prices/latest")
    assert response.status_code == 200
    data = response.json()
    
    # Vérification de la structure des données
    assert "timestamp" in data
    assert "open_price" in data
    assert "high_price" in data
    assert "low_price" in data
    assert "close_price" in data
    assert "volume" in data
    
    # Vérification des types de données
    assert isinstance(data["timestamp"], str)
    assert isinstance(data["open_price"], float)
    assert isinstance(data["high_price"], float)
    assert isinstance(data["low_price"], float)
    assert isinstance(data["close_price"], float)
    assert isinstance(data["volume"], float)

def test_historical_prices(client, sample_data):
    """Test de la récupération des prix historiques."""
    # Test avec les paramètres par défaut
    response = client.get("/api/v1/prices/historical")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 100  # Limite par défaut
    
    # Test avec une période spécifique
    today = datetime.now()
    week_ago = (today - timedelta(days=7)).strftime("%Y-%m-%d")
    response = client.get(f"/api/v1/prices/historical?start_date={week_ago}&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 10

def test_price_stats(client, sample_data):
    """Test des statistiques de prix."""
    # Test avec la période par défaut (24h)
    response = client.get("/api/v1/prices/stats")
    assert response.status_code == 200
    data = response.json()
    
    # Vérification de la structure
    assert "period" in data
    assert "min_price" in data
    assert "max_price" in data
    assert "avg_price" in data
    assert "total_volume" in data
    assert "data_points" in data
    
    # Test avec différentes périodes
    for period in ["24h", "7d", "30d"]:
        response = client.get(f"/api/v1/prices/stats?period={period}")
        assert response.status_code == 200
        data = response.json()
        assert data["period"] == period

def test_error_handling(client):
    """Test de la gestion des erreurs."""
    # Test avec une date invalide
    response = client.get("/api/v1/prices/historical?start_date=invalid_date")
    assert response.status_code == 500  # Erreur de base de données attendue
    
    # Test avec une période invalide
    response = client.get("/api/v1/prices/stats?period=invalid")
    assert response.status_code == 200  # Utilise la période par défaut (24h) 