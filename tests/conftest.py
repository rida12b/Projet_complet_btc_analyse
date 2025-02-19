import pytest
import os
import sys

# Ajout du répertoire racine au PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture(scope="session")
def project_root():
    """Retourne le chemin racine du projet"""
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

@pytest.fixture(scope="session")
def src_dir(project_root):
    """Retourne le chemin du répertoire src"""
    return os.path.join(project_root, 'src') 