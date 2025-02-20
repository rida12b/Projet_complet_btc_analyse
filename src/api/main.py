"""
Point d'entrée principal de l'API REST Bitcoin Trends.
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import sqlite3
from datetime import datetime, timedelta
import os
from typing import List, Optional
import pandas as pd
import numpy as np
import logging

from src.api.config import (
    API_TITLE,
    API_DESCRIPTION,
    API_PREFIX,
    CORS_ORIGINS,
    DOCS_URL,
    REDOC_URL,
    OPENAPI_URL
)
from src.data.config import DB_FILE
from src.models.prophet_model import BitcoinProphetModel
from src.models.config import MODEL_PATHS, LOGGING_CONFIG

# Configuration du logging
os.makedirs(os.path.dirname(LOGGING_CONFIG['filename']), exist_ok=True)
logging.basicConfig(**LOGGING_CONFIG)
logger = logging.getLogger(__name__)

# Création de l'application FastAPI
app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    docs_url=DOCS_URL,
    redoc_url=REDOC_URL,
    openapi_url=OPENAPI_URL
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Encodeur JSON personnalisé pour les types NumPy
class CustomJSONEncoder:
    @staticmethod
    def encode(obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

# Modèles de données
from pydantic import BaseModel

class PriceData(BaseModel):
    timestamp: str
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    volume: float
    volume_buy: float
    transactions: int
    transactions_buy: int

class PredictionRequest(BaseModel):
    """Modèle de requête pour les prédictions."""
    horizon: int = 7  # Nombre de jours à prédire
    return_components: bool = False  # Retourner les composantes de la prédiction

class PredictionResponse(BaseModel):
    """Modèle de réponse pour les prédictions."""
    dates: List[str]
    predictions: List[float]
    lower_bounds: List[float]
    upper_bounds: List[float]
    components: Optional[dict] = None

    class Config:
        json_encoders = {
            np.ndarray: lambda x: x.tolist(),
            np.integer: lambda x: int(x),
            np.floating: lambda x: float(x)
        }

# Fonctions utilitaires
def get_db_connection():
    """Crée une connexion à la base de données SQLite."""
    if not os.path.exists(DB_FILE):
        raise HTTPException(
            status_code=500,
            detail="Base de données non trouvée. Veuillez lancer la collecte des données."
        )
    return sqlite3.connect(DB_FILE)

# Middleware pour la gestion globale des erreurs
@app.middleware("http")
async def error_handling_middleware(request, call_next):
    """Middleware pour capturer et logger toutes les erreurs."""
    try:
        logger.info(f"Requête reçue: {request.method} {request.url}")
        response = await call_next(request)
        logger.info(f"Réponse envoyée: {response.status_code}")
        return response
    except Exception as e:
        logger.error(f"Erreur non gérée: {str(e)}")
        logger.error(f"Type d'erreur: {type(e)}")
        logger.error("Stack trace:", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": str(e)}
        )

# Routes de l'API
@app.get("/")
async def root():
    """Page d'accueil de l'API."""
    return {
        "name": API_TITLE,
        "version": "1.0.0",
        "description": "API pour l'analyse des tendances du Bitcoin"
    }

@app.get(f"{API_PREFIX}/prices/latest", response_model=PriceData)
async def get_latest_price():
    """Récupère le dernier prix du Bitcoin."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT timestamp, open_price, high_price, low_price, close_price,
                   volume, volume_buy, transactions, transactions_buy
            FROM bitcoin_prices
            ORDER BY timestamp DESC
            LIMIT 1
        """)
        
        row = cursor.fetchone()
        if not row:
            raise HTTPException(
                status_code=404,
                detail="Aucune donnée de prix disponible"
            )
            
        return PriceData(
            timestamp=row[0],
            open_price=row[1],
            high_price=row[2],
            low_price=row[3],
            close_price=row[4],
            volume=row[5],
            volume_buy=row[6],
            transactions=row[7],
            transactions_buy=row[8]
        )
        
    except sqlite3.Error as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur de base de données: {str(e)}"
        )
    finally:
        conn.close()

@app.get(f"{API_PREFIX}/prices/historical", response_model=List[PriceData])
async def get_historical_prices(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: Optional[int] = 100
):
    """
    Récupère l'historique des prix du Bitcoin.
    
    - start_date: Date de début (format: YYYY-MM-DD)
    - end_date: Date de fin (format: YYYY-MM-DD)
    - limit: Nombre maximum de résultats (défaut: 100)
    """
    conn = None
    try:
        # Valider les dates
        if start_date:
            try:
                datetime.strptime(start_date, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail="Format de date de début invalide. Utilisez YYYY-MM-DD"
                )
        
        if end_date:
            try:
                datetime.strptime(end_date, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail="Format de date de fin invalide. Utilisez YYYY-MM-DD"
                )
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT timestamp, open_price, high_price, low_price, close_price,
                   volume, volume_buy, transactions, transactions_buy
            FROM bitcoin_prices
            WHERE 1=1
        """
        params = []
        
        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date)
            
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        return [
            PriceData(
                timestamp=row[0],
                open_price=row[1],
                high_price=row[2],
                low_price=row[3],
                close_price=row[4],
                volume=row[5],
                volume_buy=row[6],
                transactions=row[7],
                transactions_buy=row[8]
            )
            for row in rows
        ]
        
    except sqlite3.Error as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur de base de données: {str(e)}"
        )
    finally:
        if conn:
            conn.close()

@app.get(f"{API_PREFIX}/prices/stats")
async def get_price_stats(period: Optional[str] = "24h"):
    """
    Récupère les statistiques des prix du Bitcoin.
    
    - period: Période d'analyse (24h, 7d, 30d)
    """
    conn = None
    try:
        # Valider la période
        if period not in ["24h", "7d", "30d"]:
            raise HTTPException(
                status_code=400,
                detail="Période invalide. Utilisez 24h, 7d ou 30d"
            )
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Calcul de la date de début selon la période
        now = datetime.now()
        if period == "7d":
            start_date = now - timedelta(days=7)
        elif period == "30d":
            start_date = now - timedelta(days=30)
        else:  # 24h par défaut
            start_date = now - timedelta(days=1)
            
        cursor.execute("""
            SELECT 
                MIN(low_price) as min_price,
                MAX(high_price) as max_price,
                AVG(close_price) as avg_price,
                SUM(volume) as total_volume,
                COUNT(*) as data_points
            FROM bitcoin_prices
            WHERE timestamp >= ?
        """, (start_date.strftime("%Y-%m-%d %H:%M:%S"),))
        
        row = cursor.fetchone()
        if not row:
            raise HTTPException(
                status_code=404,
                detail=f"Aucune donnée disponible pour la période {period}"
            )
            
        return {
            "period": period,
            "min_price": row[0],
            "max_price": row[1],
            "avg_price": row[2],
            "total_volume": row[3],
            "data_points": row[4]
        }
        
    except sqlite3.Error as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur de base de données: {str(e)}"
        )
    finally:
        if conn:
            conn.close()

# Dépendance pour le modèle Prophet
def get_prophet_model():
    """Dépendance pour obtenir une instance du modèle Prophet."""
    model = BitcoinProphetModel()
    try:
        model.load(MODEL_PATHS["PROPHET"])
    except Exception as e:
        logger.error(f"Erreur lors du chargement du modèle: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erreur lors du chargement du modèle"
        )
    return model

@app.post(f"{API_PREFIX}/predict", response_model=PredictionResponse)
async def predict_prices(request: PredictionRequest, model: BitcoinProphetModel = Depends(get_prophet_model)):
    """
    Prédit les prix futurs du Bitcoin.
    
    - horizon: Nombre de jours à prédire (entre 1 et 30)
    - return_components: Retourner les composantes de la prédiction
    """
    try:
        logger.info(f"Début de la prédiction avec horizon={request.horizon}, return_components={request.return_components}")
        logger.debug(f"Modèle reçu: {model}")
        
        # Validation de l'horizon
        if request.horizon <= 0:
            logger.warning(f"Horizon invalide: {request.horizon}")
            raise HTTPException(
                status_code=400,
                detail="L'horizon de prédiction doit être supérieur à 0"
            )
        if request.horizon > 30:
            logger.warning(f"Horizon trop grand: {request.horizon}")
            raise HTTPException(
                status_code=400,
                detail="L'horizon de prédiction ne peut pas dépasser 30 jours"
            )
        
        # Récupérer les données historiques
        try:
            conn = get_db_connection()
            logger.info("Récupération des données historiques...")
            df = pd.read_sql_query("""
                SELECT timestamp, open_price, high_price, low_price, close_price, volume
                FROM bitcoin_prices
                ORDER BY timestamp ASC;
            """, conn)
            
            if df.empty:
                logger.warning("Aucune donnée historique trouvée")
                raise HTTPException(
                    status_code=404,
                    detail="Aucune donnée historique disponible"
                )
                
            logger.info(f"Données récupérées: {len(df)} entrées")
            logger.debug(f"Colonnes disponibles: {df.columns.tolist()}")
            logger.debug(f"Premières lignes:\n{df.head()}")
            
            # Faire la prédiction
            logger.info(f"Génération des prédictions pour {request.horizon} jours...")
            try:
                forecast = model.predict(df, request.horizon)
                logger.info("Prédictions générées avec succès")
                logger.debug(f"Colonnes du forecast: {forecast.columns.tolist()}")
                logger.debug(f"Premières lignes du forecast:\n{forecast.head()}")
            except Exception as e:
                logger.error(f"Erreur lors de la génération des prédictions: {str(e)}")
                logger.error(f"Type d'erreur: {type(e)}")
                logger.error(f"Stack trace:", exc_info=True)
                raise HTTPException(
                    status_code=500,
                    detail=f"Erreur lors de la génération des prédictions: {str(e)}"
                )
            
            # Préparer la réponse
            try:
                response = {
                    "dates": forecast["ds"].dt.strftime("%Y-%m-%d %H:%M:%S").tolist(),
                    "predictions": np.expm1(forecast["yhat"]).tolist(),
                    "lower_bounds": np.expm1(forecast["yhat_lower"]).tolist(),
                    "upper_bounds": np.expm1(forecast["yhat_upper"]).tolist()
                }
                
                # Ajouter les composantes si demandées
                if request.return_components:
                    response["components"] = {
                        "trend": forecast["trend"].tolist() if "trend" in forecast else None,
                        "weekly": forecast["weekly"].tolist() if "weekly" in forecast else None,
                        "yearly": forecast["yearly"].tolist() if "yearly" in forecast else None
                    }
                
                logger.info("Réponse préparée avec succès")
                logger.debug(f"Réponse: {response}")
                return response
            except Exception as e:
                logger.error(f"Erreur lors de la préparation de la réponse: {str(e)}")
                logger.error(f"Type d'erreur: {type(e)}")
                logger.error(f"Stack trace:", exc_info=True)
                raise HTTPException(
                    status_code=500,
                    detail=f"Erreur lors de la préparation de la réponse: {str(e)}"
                )
            
        except sqlite3.Error as e:
            logger.error(f"Erreur de base de données: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Erreur lors de l'accès à la base de données: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Erreur lors de la prédiction: {str(e)}")
            logger.error(f"Type d'erreur: {type(e)}")
            logger.error(f"Stack trace:", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Erreur lors de la prédiction: {str(e)}"
            )
            
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Erreur inattendue: {str(e)}")
        logger.error(f"Type d'erreur: {type(e)}")
        logger.error(f"Stack trace:", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Erreur inattendue: {str(e)}"
        )
    finally:
        if 'conn' in locals():
            conn.close()
            logger.info("Connexion à la base de données fermée")

@app.get(f"{API_PREFIX}/model/info")
async def get_model_info():
    """Récupère les informations sur le modèle."""
    try:
        # Charger le modèle
        model = BitcoinProphetModel()
        try:
            model.load(MODEL_PATHS["PROPHET"])
        except Exception as e:
            logger.error(f"Erreur lors du chargement du modèle: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Erreur lors du chargement du modèle: {str(e)}"
            )
        
        # Récupérer les paramètres du modèle
        params = {
            "changepoint_prior_scale": model.model.changepoint_prior_scale,
            "seasonality_prior_scale": model.model.seasonality_prior_scale,
            "holidays_prior_scale": model.model.holidays_prior_scale,
            "daily_seasonality": model.model.daily_seasonality,
            "weekly_seasonality": model.model.weekly_seasonality,
            "yearly_seasonality": model.model.yearly_seasonality
        }
        
        # Récupérer les métriques (à implémenter)
        metrics = {
            "rmse": None,
            "mae": None,
            "mape": None
        }
        
        return {
            "name": "Prophet",
            "version": "1.0.0",
            "parameters": params,
            "metrics": metrics,
            "last_training": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "features": ["close_price", "timestamp"]
        }
        
    except Exception as e:
        logger.error(f"Erreur inattendue: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur inattendue: {str(e)}"
        ) 