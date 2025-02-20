"""
Application web Streamlit pour l'analyse des tendances du Bitcoin.
"""
import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Chargement des variables d'environnement
load_dotenv()

# Configuration de Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyD-fBwFIxlNKIUPw-c0QTItBeij8PlItio")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

# Configuration de l'API
API_URL = "http://localhost:8000/api/v1"

# Configuration de la page
st.set_page_config(
    page_title="Analyse des Tendances du Bitcoin",
    page_icon="📈",
    layout="wide"
)

# Titre et description
st.title("📊 Analyse des Tendances du Bitcoin")
st.markdown("""
Cette application affiche l'historique du Bitcoin sur 3 mois et permet d'analyser
la tendance des dernières 24 heures.
""")

def get_latest_price():
    """Récupère le dernier prix du Bitcoin."""
    try:
        st.write("Tentative de récupération du prix...")  # Debug log
        response = requests.get(f"{API_URL}/prices/latest")
        st.write(f"Status code: {response.status_code}")  # Debug log
        
        if response.status_code == 200:
            data = response.json()
            st.write(f"Données reçues: {data}")  # Debug log
            return data["close_price"], data["close_price"] - data["open_price"]
        else:
            st.error(f"Erreur API: {response.text}")
            return 0, 0
    except Exception as e:
        st.error(f"Erreur lors de la récupération du prix : {str(e)}")
        return 0, 0

def get_historical_data(days=90):
    """Récupère l'historique des données."""
    try:
        st.write("Tentative de récupération des données historiques...")  # Debug log
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        st.write(f"Dates demandées : du {start_date} au {end_date}")  # Debug log
        
        response = requests.get(
            f"{API_URL}/prices/historical",
            params={
                "start_date": start_date,
                "end_date": end_date,
                "limit": days * 24  # Données horaires
            }
        )
        
        st.write(f"Status code historique: {response.status_code}")  # Debug log
        
        if response.status_code == 200:
            data = pd.DataFrame(response.json())
            data['timestamp'] = pd.to_datetime(data['timestamp'])
            st.write(f"Nombre de données reçues: {len(data)}")  # Debug log
            return data
        else:
            st.error(f"Erreur API historique: {response.text}")
            return pd.DataFrame()
            
    except Exception as e:
        st.error(f"Erreur lors de la récupération des données : {str(e)}")
        return pd.DataFrame()

def analyze_with_gemini(data):
    """Analyse les données avec Gemini."""
    try:
        # Préparation des données pour l'analyse
        last_24h = data.tail(24)
        opening_price = last_24h['open_price'].iloc[0]
        closing_price = last_24h['close_price'].iloc[-1]
        highest_price = last_24h['high_price'].max()
        lowest_price = last_24h['low_price'].min()
        volume_total = last_24h['volume'].sum()
        percent_change = ((closing_price / opening_price - 1) * 100)

        # Construction du prompt pour Gemini
        prompt = f"""En tant qu'expert en analyse technique du Bitcoin, analyse les données suivantes des dernières 24 heures :

Prix d'ouverture : ${opening_price:,.2f}
Prix de clôture : ${closing_price:,.2f}
Plus haut : ${highest_price:,.2f}
Plus bas : ${lowest_price:,.2f}
Variation : {percent_change:,.2f}%
Volume total : ${volume_total:,.0f}

Fournis une analyse détaillée incluant :
1. La tendance générale (haussière/baissière)
2. Les points de support et de résistance importants
3. Une recommandation sur la direction probable du prix
4. Les risques potentiels à surveiller

Limite ta réponse à 4-5 phrases concises."""

        # Appel à l'API Gemini
        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        return f"Erreur lors de l'analyse : {str(e)}"

def prepare_analysis_data(data):
    """Prépare les données des dernières 24h pour l'analyse."""
    last_24h = data.tail(24).copy()
    
    # Calculs des métriques
    metrics = {
        'open_price': last_24h['open_price'].iloc[0],
        'high_price': last_24h['high_price'].max(),
        'low_price': last_24h['low_price'].min(),
        'close_price': last_24h['close_price'].iloc[-1],
        'percent_change': ((last_24h['close_price'].iloc[-1] / last_24h['open_price'].iloc[0] - 1) * 100),
        'volume_total': last_24h['volume'].sum()
    }
    
    # Analyse avec Gemini
    analysis = analyze_with_gemini(data)
    
    # Formatage du résumé
    summary = f"""📊 Résumé technique (24h) :
    
Prix d'ouverture : ${metrics['open_price']:,.2f}
Prix le plus haut : ${metrics['high_price']:,.2f}
Prix le plus bas : ${metrics['low_price']:,.2f}
Prix de clôture : ${metrics['close_price']:,.2f}
Variation : {metrics['percent_change']:,.2f}%
Volume total : ${metrics['volume_total']:,.0f}

🤖 Analyse IA :
{analysis}
"""
    return summary

# Prix actuel
price, change = get_latest_price()
col1, col2 = st.columns([2, 1])
with col1:
    st.metric(
        "Prix actuel",
        f"${price:,.2f}",
        f"{change:+.2f}",
        delta_color="normal"
    )

# Données historiques
historical_data = get_historical_data()
if not historical_data.empty:
    # Graphique principal (3 mois)
    st.subheader("📈 Historique du Bitcoin (3 mois)")
    fig = go.Figure(data=[go.Candlestick(
        x=historical_data['timestamp'],
        open=historical_data['open_price'],
        high=historical_data['high_price'],
        low=historical_data['low_price'],
        close=historical_data['close_price'],
        name="OHLC"
    )])
    
    fig.update_layout(
        yaxis_title="Prix (USD)",
        xaxis_title="Date",
        height=600,
        template="plotly_dark",
        xaxis_rangeslider_visible=False
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Section d'analyse des dernières 24h
    st.subheader("🔍 Analyse des dernières 24 heures")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        # Graphique des dernières 24h
        last_24h = historical_data.tail(24)
        fig_24h = go.Figure(data=[go.Candlestick(
            x=last_24h['timestamp'],
            open=last_24h['open_price'],
            high=last_24h['high_price'],
            low=last_24h['low_price'],
            close=last_24h['close_price'],
            name="OHLC"
        )])
        
        fig_24h.update_layout(
            title="Dernières 24 heures",
            yaxis_title="Prix (USD)",
            xaxis_title="Heure",
            height=400,
            template="plotly_dark",
            xaxis_rangeslider_visible=False
        )
        
        st.plotly_chart(fig_24h, use_container_width=True)
    
    with col2:
        st.markdown("### 📊 Résumé")
        if st.button("Analyser la tendance"):
            with st.spinner("Analyse en cours avec Gemini..."):
                analysis = prepare_analysis_data(historical_data)
                st.markdown(analysis)
else:
    st.error("Aucune donnée disponible")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p>Données mises à jour toutes les heures</p>
</div>
""", unsafe_allow_html=True) 