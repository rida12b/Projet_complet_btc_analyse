# Documentation du Projet : Analyse des Tendances du Bitcoin avec IA & Open Data

## 📋 Présentation Générale

### Objectif du Projet
Développement d'une solution complète d'analyse des tendances du Bitcoin combinant :
- Collecte de données en temps réel
- Analyse par Intelligence Artificielle
- Interface web interactive
- API REST
- Monitoring et déploiement continu

### Technologies Utilisées
- **Backend** : FastAPI, SQLite, Python
- **Frontend** : Streamlit
- **IA** : Google Gemini Pro
- **Data** : Coinalyze API
- **DevOps** : GitHub Actions, Docker
- **Monitoring** : Prometheus, Grafana

## 🎯 Réponse au Référentiel

### E1 - Gestion des Données
#### Réalisations
1. **Collecte Multi-Sources**
   - API Coinalyze pour les données OHLCV
   - Stockage SQLite avec schéma optimisé
   - Mise à jour horaire automatisée

2. **Base de Données**
   - Structure : `bitcoin_prices` (OHLCV + métriques)
   - Indexation pour performances optimales
   - Gestion des doublons et données manquantes

3. **API REST**
   - Endpoints `/prices/historical` et `/prices/latest`
   - Documentation OpenAPI
   - Tests unitaires et d'intégration

#### Code Source
- `src/data/collector.py` : Collecteur de données
- `src/data/config.py` : Configuration
- `tests/test_collector.py` : Tests unitaires

### E2 - Veille et Service IA
#### Réalisations
1. **Benchmark IA**
   - Migration de Prophet vers Gemini Pro
   - Amélioration des analyses en temps réel
   - Optimisation des prompts

2. **Intégration IA**
   - API Gemini pour l'analyse technique
   - Formatage personnalisé des réponses
   - Gestion du contexte et des erreurs

#### Documentation Technique
- Prompts optimisés dans `src/web/app.py`
- Configuration dans les variables d'environnement
- Tests dans `tests/test_api.py`

### E3 - API et Tests
#### Réalisations
1. **API REST**
   - Architecture FastAPI
   - Endpoints documentés
   - Gestion des erreurs

2. **Tests**
   - Tests unitaires (pytest)
   - Tests d'intégration
   - Mocks pour l'IA

#### Points Clés
- Couverture de tests > 80%
- Documentation OpenAPI
- Logging complet

### E4 - Application Web
#### Réalisations
1. **Interface Streamlit**
   - Graphiques interactifs (Plotly)
   - Analyse en temps réel
   - Design responsive

2. **Fonctionnalités**
   - Historique 3 mois
   - Analyse 24h
   - Prédictions IA

#### Architecture
- Frontend : Streamlit
- Backend : FastAPI
- Base de données : SQLite

### E5 - Monitoring
#### Réalisations
1. **Logging**
   - Logs structurés
   - Rotation des logs
   - Niveaux de verbosité

2. **Métriques**
   - Temps de réponse API
   - Utilisation ressources
   - Erreurs et exceptions

## 🔧 Architecture Technique

### Structure du Projet
```
projet_final_simplon/
├── src/
│   ├── api/          # API REST
│   ├── data/         # Collecte et stockage
│   ├── models/       # Modèles IA
│   └── web/          # Interface Streamlit
├── tests/            # Tests
├── docs/             # Documentation
└── data/             # Données SQLite
```

### Flux de Données
1. Collecte (Coinalyze) → SQLite
2. API REST → Streamlit
3. Gemini → Analyse
4. Interface → Utilisateur

## 📈 Métriques et Performance

### Performances
- Temps réponse API < 100ms
- Mise à jour données : 1h
- Analyse IA : 2-3s

### Volumétrie
- 3 mois de données
- ~2160 points horaires
- ~90 requêtes/minute

## 🚀 Déploiement

### Prérequis
- Python 3.9+
- Clés API (Coinalyze, Gemini)
- SQLite

### Installation
```bash
git clone https://github.com/rida12b/Projet_complet_btc_analyse.git
cd projet_final_simplon
pip install -r requirements.txt
```

### Configuration
1. Créer `.env` avec les clés API
2. Configurer les paramètres dans `config.py`
3. Lancer la collecte initiale

### Lancement
```bash
# API
python src/api/run_api.py

# Interface
streamlit run src/web/app.py
```

## 📝 Maintenance

### Mises à Jour
1. Vérifier les dépendances
2. Exécuter les tests
3. Déployer via GitHub Actions

### Backup
- Sauvegarde quotidienne DB
- Export données CSV
- Logs archivés

## 🔍 Points d'Amélioration

### Futures Évolutions
1. Machine Learning avancé
2. Alertes personnalisées
3. Interface mobile

### Optimisations
1. Cache Redis
2. Scaling horizontal
3. Analyses prédictives

## 📚 Documentation Annexe

### Guides
- Installation détaillée
- Contribution
- Déploiement

### API Reference
- Endpoints
- Modèles de données
- Exemples

## 🔐 Sécurité

### Mesures
1. Rate limiting
2. Validation données
3. Logs sécurisés

### Conformité
- RGPD
- Sécurité API
- Authentification

## 📊 Suivi du Projet

### Versions
- v0.1.0 : MVP
- v0.2.0 : Migration Gemini
- v0.3.0 : Interface améliorée

### Changelog
[Voir suivi_projet.md] 