# Backlog du Projet Bitcoin Trends

## 📋 User Stories

### 🔴 Priorité Haute

#### Collecte et Stockage des Données
- **US1** : En tant qu'utilisateur, je veux voir les données historiques du Bitcoin pour analyser les tendances passées
  - Collecter les données via l'API CoinGecko
  - Stocker les données dans une base de données
  - Afficher un graphique historique des prix
  - *Estimation : 3 points*
  - *Critères d'acceptation* :
    - Données sur au moins 1 an
    - Mise à jour quotidienne
    - Temps de réponse < 2s

#### Prédiction IA
- **US2** : En tant qu'utilisateur, je veux obtenir des prédictions sur le prix futur du Bitcoin
  - Développer un modèle de prédiction
  - Entraîner le modèle sur les données historiques
  - Exposer les prédictions via une API
  - *Estimation : 5 points*
  - *Critères d'acceptation* :
    - Précision > 70%
    - Prédictions sur 7 jours
    - Intervalle de confiance

### 🟡 Priorité Moyenne

#### Interface Utilisateur
- **US3** : En tant qu'utilisateur, je veux une interface web intuitive pour visualiser les données
  - Créer un dashboard interactif
  - Implémenter des filtres de date
  - Ajouter des indicateurs techniques
  - *Estimation : 3 points*
  - *Critères d'acceptation* :
    - Interface responsive
    - Temps de chargement < 3s
    - Compatible avec les principaux navigateurs

#### Alertes et Notifications
- **US4** : En tant qu'utilisateur, je veux être alerté des mouvements significatifs du prix
  - Définir des seuils d'alerte
  - Implémenter un système de notifications
  - *Estimation : 2 points*
  - *Critères d'acceptation* :
    - Alertes en temps réel
    - Personnalisation des seuils
    - Notifications par email/web

### 🟢 Priorité Basse

#### Analyse Technique
- **US5** : En tant qu'utilisateur, je veux accéder à des indicateurs techniques avancés
  - Calculer les moyennes mobiles
  - Implémenter RSI, MACD
  - Visualiser les supports/résistances
  - *Estimation : 3 points*
  - *Critères d'acceptation* :
    - Précision des calculs
    - Mise à jour en temps réel
    - Documentation des indicateurs

#### Export et Rapports
- **US6** : En tant qu'utilisateur, je veux pouvoir exporter les données et analyses
  - Export en CSV/PDF
  - Génération de rapports personnalisés
  - *Estimation : 2 points*
  - *Critères d'acceptation* :
    - Multiples formats d'export
    - Personnalisation des rapports
    - Temps d'export < 30s

## 📅 Planification des Sprints

### Sprint 1 - Fondations
- US1 : Collecte et stockage des données
- Mise en place de l'infrastructure

### Sprint 2 - Intelligence Artificielle
- US2 : Développement du modèle de prédiction
- Tests et validation du modèle

### Sprint 3 - Interface Utilisateur
- US3 : Développement du dashboard
- Intégration des données en temps réel

### Sprint 4 - Fonctionnalités Avancées
- US4 : Système d'alertes
- US5 : Indicateurs techniques (début)

### Sprint 5 - Finalisation
- US5 : Finalisation des indicateurs
- US6 : Export et rapports
- Tests utilisateurs

## 📊 Métriques de Suivi
- Vélocité cible par sprint : 8 points
- Durée du sprint : 2 semaines
- Temps de développement total estimé : 10 semaines 