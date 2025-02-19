"""
Script d'exécution de la collecte des données en continu.
"""
import time
import signal
import sys
from collector import BitcoinDataCollector
from config import UPDATE_INTERVAL

def signal_handler(signum, frame):
    """Gestionnaire de signal pour arrêter proprement le script."""
    print("\nArrêt du collecteur...")
    sys.exit(0)

def main():
    """Fonction principale d'exécution."""
    # Configuration du gestionnaire de signal pour Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    collector = BitcoinDataCollector()
    print(f"Démarrage de la collecte (intervalle: {UPDATE_INTERVAL} secondes)")
    
    try:
        while True:
            try:
                collector.collect_data()
            except Exception as e:
                print(f"Erreur lors de la collecte: {str(e)}")
            
            # Attente avant la prochaine collecte
            time.sleep(UPDATE_INTERVAL)
    finally:
        collector.close()

if __name__ == "__main__":
    main() 