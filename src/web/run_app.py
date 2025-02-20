"""
Script de lancement de l'application web Streamlit.
"""
import os
import streamlit.web.cli as stcli
from src.web.config import API_HOST, API_PORT

def run_streamlit():
    """Lance l'application Streamlit."""
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, 'app.py')
    args = [
        "streamlit",
        "run",
        filename,
        "--server.port=8501",  # Port par défaut de Streamlit
        "--server.address=localhost",
        f"--server.baseUrlPath={os.getenv('STREAMLIT_BASE_URL', '')}",
        "--browser.serverAddress=localhost",
        "--theme.base=dark"
    ]
    sys.argv = args
    sys.exit(stcli.main())

if __name__ == "__main__":
    import sys
    run_streamlit() 