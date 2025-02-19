import os
import pytest

def test_project_structure():
    """Vérifie que la structure du projet est correcte"""
    required_directories = [
        'src',
        'src/data',
        'src/models',
        'src/api',
        'src/web',
        'tests',
        'docs'
    ]
    
    required_files = [
        'README.md',
        'requirements.txt',
        '.gitignore',
        'suivi_projet.md'
    ]
    
    # Vérification des répertoires
    for directory in required_directories:
        assert os.path.isdir(directory), f"Le répertoire {directory} n'existe pas"
    
    # Vérification des fichiers
    for file in required_files:
        assert os.path.isfile(file), f"Le fichier {file} n'existe pas"
        
def test_gitignore_content():
    """Vérifie que .gitignore contient les entrées essentielles"""
    required_ignores = [
        'venv/',
        '__pycache__/',
        '.env',
        '*.log',
        '.coverage'
    ]
    
    with open('.gitignore', 'r') as f:
        content = f.read()
        
    for ignore in required_ignores:
        assert ignore in content, f"L'entrée {ignore} manque dans .gitignore" 