# Suivi du Projet : Analyse des Tendances du Bitcoin avec IA & Open Data

## 📋 Description du Projet
Développement d'une solution d'analyse des tendances du Bitcoin utilisant l'intelligence artificielle et les données ouvertes, avec une API REST et une interface web.

## 📊 État d'Avancement Global
- Phase 0 : 🟢 Terminé (100%)
- Phase 1 : 🟢 Terminé (100%)
- Phase 2 : 🟢 Terminé (100%)
  - ✅ Collecte des données
  - ✅ Base de données
  - ✅ API de données
- Phase 3 : 🟡 En cours (45%)
  - ✅ Documentation de veille initiale
  - 🟡 Tests des solutions IA
    - ✅ Structure des modèles
    - 🟡 Pipeline de test Prophet
    - ⚪ Pipeline de test LSTM
  - ⚪ Sélection finale
- Phase 4 : ⚪ Non commencé
- Phase 5 : ⚪ Non commencé
- Phase 6 : ⚪ Non commencé

## 📝 To-Do List Globale
### Phase 0 - Mise en place (Terminé)
- [x] Création du fichier de suivi
- [x] Mise en place de l'environnement de développement
- [x] Création de la structure du projet
- [x] Configuration du gestionnaire de version (Git)
- [x] Création des tests initiaux
- [x] Création du backlog initial
- [x] Installation complète des dépendances
- [x] Configuration des outils de gestion de projet

### Phase 1 - Conception et modélisation
- [x] Rédaction des spécifications fonctionnelles
- [x] Création des diagrammes de données
- [x] Définition de l'architecture technique
- [x] Documentation RGPD

### Phase 2 - Collecte & Gestion des Données
- [ ] Développement des scripts de collecte
- [ ] Mise en place de la base de données
- [ ] Création de l'API de données

### Phase 3 - Veille & Benchmark IA
- [ ] Documentation de veille technique
- [ ] Tests des différentes solutions IA
- [ ] Sélection et configuration du service IA

### Phase 4 - API IA
- [ ] Développement de l'API du modèle
- [ ] Tests et validation
- [ ] Documentation de l'API

### Phase 5 - Application Web
- [ ] Développement des interfaces
- [ ] Intégration de l'API
- [ ] Tests utilisateurs

### Phase 6 - Monitoring
- [ ] Mise en place des outils de monitoring
- [ ] Configuration des alertes
- [ ] Documentation de maintenance

## 🛑 Suivi des Erreurs
### Erreur #1 - Installation des dépendances (19/02/2024) - RÉSOLU ✅
- **Type** : Erreur d'environnement
- **Message** : Erreur lors de l'installation des packages Python
- **Contexte** : Installation des dépendances avec pip
- **Cause** : Problèmes de compilation/installation de certains packages
- **Solutions tentées** :
  1. Installation via pip install -r requirements.txt ❌
  2. Installation des packages un par un ✅
- **Solution finale** : 
  1. Mise à jour du fichier requirements.txt
  2. Installation des packages individuellement
  3. Vérification via les tests automatisés

### Erreur #2 - Problèmes de collecte de données (19/02/2024) - RÉSOLU ✅
- **Type** : Erreur API et Base de données
- **Message** : 
  1. API Coinalyze : "Aucune donnée reçue de Coinalyze"
  2. PostgreSQL : "'utf-8' codec can't decode byte 0xe9 in position 84: invalid continuation byte"
- **Contexte** : 
  - Exécution des tests de collecte de données
  - Tentative de connexion à l'API Coinalyze
  - Tentative de connexion à PostgreSQL
- **Causes** :
  1. API Coinalyze : Problème de format de réponse et de paramètres
  2. PostgreSQL : Problème d'encodage des caractères spéciaux
- **Solutions tentées** :
  1. API Coinalyze :
     - Modification du format des paramètres ✅
     - Ajout de la gestion des erreurs ✅
  2. Base de données :
     - Tentatives avec PostgreSQL (différents encodages) ❌
     - Migration vers SQLite ✅
- **Solution finale** : 
  1. API Coinalyze :
     - Utilisation du bon format de timestamp
     - Gestion appropriée des paramètres de l'API
  2. Base de données :
     - Remplacement de PostgreSQL par SQLite
     - Avantages :
       - Plus léger (pas de serveur nécessaire)
       - Configuration simple
       - Base de données fichier unique
       - Pas de problème d'encodage
     - Modifications :
       - Adaptation des types de données
       - Simplification de la connexion
       - Mise à jour des requêtes SQL
     - Validation par les tests :
       - ✅ test_api_connection
       - ✅ test_database_connection
       - ✅ test_data_collection

## 📈 Comptes-rendus des Phases
### Phase 0 - Initialisation (19/02/2024) - Mise à jour
Actions réalisées :
1. Création de la structure initiale du projet
2. Mise en place des fichiers de base :
   - README.md avec documentation initiale
   - requirements.txt avec les dépendances
   - .gitignore pour exclure les fichiers non nécessaires
3. Initialisation du dépôt Git
4. Mise en place des tests initiaux :
   - ✅ Test de la version Python (3.13.1)
   - ✅ Test de la structure du projet
   - ✅ Test du contenu .gitignore
   - ✅ Test des dépendances
5. Installation réussie des packages requis :
   - scikit-learn
   - numpy
   - requests
   - python-binance
   - pytest
   - pytest-cov
   - prometheus-client
   - sphinx

Documentation créée :
- `docs/backlog.md` : User stories et planification
- `docs/specifications.md` : Spécifications fonctionnelles détaillées

Problèmes rencontrés :
- Difficultés avec l'installation des packages Python
- Nécessité de mettre à jour l'environnement de build

Structure mise en place :
```
projet_bitcoin/
├── .git/
├── .gitignore
├── README.md
├── suivi_projet.md
├── requirements.txt
├── src/
│   ├── data/
│   ├── models/
│   ├── api/
│   └── web/
├── tests/
│   ├── conftest.py
│   ├── test_environment.py
│   └── test_project_structure.py
└── docs/
    ├── backlog.md
    └── specifications.md
```

### Phase 1 - Conception (19/02/2024)
Actions réalisées :
1. Création du backlog et des spécifications :
   - Définition des user stories
   - Priorisation des fonctionnalités
   - Planification des sprints
   - Rédaction des spécifications détaillées

2. Modélisation des données :
   - Création du MCD
   - Définition du MPD
   - Scripts SQL de création
   - Documentation RGPD

3. Architecture technique :
   - Architecture globale
   - Description des services
   - Infrastructure et déploiement
   - Sécurité et scalabilité

4. Documentation RGPD :
   - Registre des traitements
   - Mesures techniques
   - Droits des utilisateurs
   - Procédures de conformité

Documentation créée :
- `docs/backlog.md` : User stories et planification
- `docs/specifications.md` : Spécifications fonctionnelles
- `docs/data_model.md` : Modélisation des données
- `docs/architecture.md` : Architecture technique
- `docs/rgpd.md` : Documentation RGPD

Structure finale de la documentation :
```
projet_bitcoin/
├── .git/
├── .gitignore
├── README.md
├── suivi_projet.md
├── requirements.txt
├── src/
│   ├── data/
│   ├── models/
│   ├── api/
│   └── web/
├── tests/
│   ├── conftest.py
│   ├── test_environment.py
│   └── test_project_structure.py
└── docs/
    ├── backlog.md
    ├── specifications.md
    ├── data_model.md
    ├── architecture.md
    └── rgpd.md
```

### Phase 2 - Collecte & Gestion des Données (19/02/2024)
Actions réalisées :
1. Mise en place de la collecte de données :
   - Intégration de l'API Coinalyze
   - Configuration des paramètres de collecte :
     - Intervalle : 1 minute (pour plus de précision)
     - Fenêtre de collecte : dernière heure
     - Mise à jour en temps réel
   - Gestion des erreurs et logging

2. Mise en place de la base de données :
   - Choix de SQLite comme solution de stockage
   - Création du schéma de données
   - Implémentation des requêtes d'insertion
   - Optimisation avec index sur timestamp

3. Développement de l'API REST :
   - Création de l'API avec FastAPI
   - Endpoints implémentés :
     - `/api/v1/prices/latest` : Dernier prix (temps réel)
     - `/api/v1/prices/historical` : Historique des prix
     - `/api/v1/prices/stats` : Statistiques
   - Documentation OpenAPI/Swagger
   - Gestion des erreurs et validation
   - Tests unitaires

4. Améliorations apportées :
   - Correction du format des timestamps
   - Précision accrue des données (intervalle 1min)
   - Mise à jour en temps réel
   - Gestion des fuseaux horaires (UTC)

5. Structure mise en place :
```
src/
├── data/
│   ├── __init__.py
│   ├── config.py        # Configuration (API, DB, logging)
│   ├── collector.py     # Collecteur de données
│   └── run_collector.py # Script d'exécution
└── api/
    ├── __init__.py
    ├── config.py        # Configuration de l'API REST
    ├── main.py         # Points d'entrée de l'API
    └── run_api.py      # Script de lancement
```

6. Fonctionnalités implémentées :
   - Collecte des données OHLCV du Bitcoin
   - Stockage en base de données SQLite
   - API REST avec documentation
   - Tests automatisés

### Phase 3 - Veille & Benchmark IA (19/02/2024)
Actions réalisées :
1. Documentation de veille technique :
   - Analyse des solutions disponibles :
     - Deep Learning (LSTM, GRU)
     - Modèles statistiques (Prophet, ARIMA)
     - Solutions cloud (Azure ML, AWS SageMaker)
   - Définition des critères de sélection
   - Planification des tests

2. Prochaines étapes :
   - Implémentation des modèles sélectionnés
   - Tests de performance
   - Comparaison des résultats
   - Choix final de la solution

Documentation créée :
- `docs/veille_technique.md` : Analyse détaillée des solutions IA

## 🔄 Prochaines Actions
1. Phase 3 - Suite :
   - Implémenter le pipeline de test
   - Tester les modèles LSTM et Prophet
   - Évaluer les performances
   - Documenter les résultats

2. Préparation des données :
   - Feature engineering
   - Création des jeux d'entraînement/test
   - Calcul des indicateurs techniques 

## 📁 Structure du Projet

```
projet_final_simplon/
├── src/
│   ├── data/
│   │   ├── collector.py
│   │   └── database.py
│   ├── models/
│   │   ├── config.py          # Configuration des modèles
│   │   ├── utils.py           # Fonctions utilitaires
│   │   ├── base_model.py      # Classe de base abstraite
│   │   └── prophet_model.py   # Implémentation de Prophet
│   └── api/
│       └── main.py
├── tests/
├── docs/
│   └── veille_technique.md
└── requirements.txt
```

## 🔄 Dernières Modifications

### Implémentation du Pipeline de Test Prophet (19/02/2025)
1. Création du script de test `tests/test_prophet_model.py`
2. Objectifs des tests :
   - Validation du prétraitement des données
   - Test de l'entraînement du modèle
   - Évaluation des prédictions
   - Vérification de la sauvegarde/chargement
3. Métriques à évaluer :
   - RMSE (Root Mean Square Error)
   - MAE (Mean Absolute Error)
   - MAPE (Mean Absolute Percentage Error)
   - R2 Score

### Prochaine Étape
Exécuter les tests Prophet et analyser les résultats pour valider la performance du modèle.

## 🛑 Suivi des Erreurs
Aucune erreur majeure à signaler pour le moment.

## 📝 Notes Techniques
- La structure modulaire permettra d'ajouter facilement d'autres modèles (LSTM, etc.)
- Les métriques d'évaluation incluent RMSE, MAE, MAPE et R2
- Utilisation de logging pour le suivi des erreurs et du processus d'entraînement
- Configuration flexible des paramètres des modèles via le fichier config.py 