"""
Configuration de l'API REST Bitcoin Trends.
"""
import os
from dotenv import load_dotenv

# Chargement des variables d'environnement
load_dotenv()

# Configuration de l'API
API_VERSION = "v1"
API_PREFIX = f"/api/{API_VERSION}"
API_TITLE = "Bitcoin Trends API"
API_DESCRIPTION = """
API REST pour l'accès aux données historiques et temps réel du Bitcoin.
Permet de récupérer les prix, volumes et autres indicateurs.
"""
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))

# Configuration CORS
CORS_ORIGINS = [
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:3000",  # Pour le frontend React/Next.js
    "http://localhost:8501",  # Pour Streamlit
]

# Configuration de la documentation
DOCS_URL = "/docs"
REDOC_URL = "/redoc"
OPENAPI_URL = "/openapi.json"

# Limites de l'API
RATE_LIMIT = "100/minute"  # Limite de requêtes par minute
CACHE_EXPIRATION = 60  # Durée de cache en secondes 