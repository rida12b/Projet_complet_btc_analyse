"""
Configuration du package Bitcoin Trends.
"""
from setuptools import setup, find_packages

setup(
    name="bitcoin_trends",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.100.0",
        "uvicorn>=0.23.0",
        "python-dotenv>=1.0.0",
        "requests>=2.31.0",
        "SQLAlchemy>=2.0.0",
        "pydantic>=2.0.0",
    ],
    python_requires=">=3.8",
) 