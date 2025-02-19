import sys
import importlib.metadata
import pytest

def test_python_version():
    """Vérifie que la version de Python est 3.8 ou supérieure"""
    assert sys.version_info >= (3, 8), "Python 3.8 ou supérieur est requis"

def test_required_packages():
    """Vérifie que les packages requis sont installés"""
    required_packages = [
        'scikit-learn',
        'numpy',
        'requests',
        'python-binance',
        'pytest',
        'pytest-cov',
        'prometheus-client',
        'sphinx'
    ]
    
    for package in required_packages:
        try:
            importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            pytest.fail(f"Package {package} n'est pas installé") 