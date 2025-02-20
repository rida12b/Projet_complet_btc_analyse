"""
Configuration de l'application web Streamlit.
"""

# Configuration de l'API
API_HOST = "localhost"
API_PORT = 8000
API_VERSION = "v1"
API_URL = f"http://{API_HOST}:{API_PORT}/api/{API_VERSION}"

# Configuration de l'interface
PAGE_TITLE = "Bitcoin Trends Analysis"
PAGE_ICON = "📈"
LAYOUT = "wide"

# Configuration des graphiques
THEME = "plotly_dark"
COLORS = {
    "primary": "#1f77b4",
    "secondary": "#ff7f0e",
    "success": "#2ca02c",
    "danger": "#d62728",
    "warning": "#ffbb00",
    "info": "#17becf"
}

# Configuration des périodes
DEFAULT_HISTORICAL_PERIOD = 30  # jours
MAX_HISTORICAL_PERIOD = 90     # jours
MIN_HISTORICAL_PERIOD = 7      # jours

DEFAULT_PREDICTION_HORIZON = 7  # jours
MAX_PREDICTION_HORIZON = 30    # jours
MIN_PREDICTION_HORIZON = 1     # jour

# Configuration du cache
CACHE_TTL = 300  # secondes (5 minutes) 