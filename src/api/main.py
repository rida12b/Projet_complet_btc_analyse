"""
Point d'entrée principal de l'API REST Bitcoin Trends.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import sqlite3
from datetime import datetime, timedelta
import os
from typing import List, Optional

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

# Fonctions utilitaires
def get_db_connection():
    """Crée une connexion à la base de données SQLite."""
    if not os.path.exists(DB_FILE):
        raise HTTPException(
            status_code=500,
            detail="Base de données non trouvée. Veuillez lancer la collecte des données."
        )
    return sqlite3.connect(DB_FILE)

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
    try:
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
        conn.close()

@app.get(f"{API_PREFIX}/prices/stats")
async def get_price_stats(period: Optional[str] = "24h"):
    """
    Récupère les statistiques des prix du Bitcoin.
    
    - period: Période d'analyse (24h, 7d, 30d)
    """
    try:
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
        conn.close() 