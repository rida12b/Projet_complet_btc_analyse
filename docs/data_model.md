# Modélisation des Données - Bitcoin Trends

## 1. Modèle Conceptuel de Données (MCD)

### 1.1 Entités Principales

#### PRIX_BITCOIN
- ID (PK)
- Timestamp
- Prix_USD
- Volume_24h
- Market_Cap
- Variation_24h

#### PREDICTION
- ID (PK)
- Timestamp
- Prix_Predit
- Intervalle_Confiance_Bas
- Intervalle_Confiance_Haut
- Score_Confiance
- ID_Modele (FK)

#### MODELE
- ID (PK)
- Nom
- Version
- Date_Creation
- Metriques_Performance
- Parametres
- Statut

#### INDICATEUR_TECHNIQUE
- ID (PK)
- Timestamp
- Type
- Valeur
- Parametres
- ID_Prix (FK)

#### ALERTE
- ID (PK)
- ID_Utilisateur (FK)
- Type
- Condition
- Valeur_Seuil
- Statut
- Date_Creation
- Date_Derniere_Notification

#### UTILISATEUR
- ID (PK)
- Email
- Hash_Mot_de_Passe
- Date_Inscription
- Preferences_Notification

## 2. Modèle Physique de Données (MPD)

### 2.1 Tables

```sql
-- Table des prix Bitcoin
CREATE TABLE prix_bitcoin (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    prix_usd DECIMAL(18,8) NOT NULL,
    volume_24h DECIMAL(24,8),
    market_cap DECIMAL(24,8),
    variation_24h DECIMAL(8,4)
);

-- Table des prédictions
CREATE TABLE prediction (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    prix_predit DECIMAL(18,8) NOT NULL,
    intervalle_confiance_bas DECIMAL(18,8),
    intervalle_confiance_haut DECIMAL(18,8),
    score_confiance DECIMAL(5,4),
    id_modele INTEGER REFERENCES modele(id),
    date_creation TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Table des modèles
CREATE TABLE modele (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    version VARCHAR(50) NOT NULL,
    date_creation TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    metriques_performance JSONB,
    parametres JSONB,
    statut VARCHAR(20) DEFAULT 'actif'
);

-- Table des indicateurs techniques
CREATE TABLE indicateur_technique (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    type VARCHAR(50) NOT NULL,
    valeur DECIMAL(18,8) NOT NULL,
    parametres JSONB,
    id_prix BIGINT REFERENCES prix_bitcoin(id)
);

-- Table des utilisateurs
CREATE TABLE utilisateur (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hash_mot_de_passe VARCHAR(255) NOT NULL,
    date_inscription TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    preferences_notification JSONB
);

-- Table des alertes
CREATE TABLE alerte (
    id SERIAL PRIMARY KEY,
    id_utilisateur INTEGER REFERENCES utilisateur(id),
    type VARCHAR(50) NOT NULL,
    condition VARCHAR(50) NOT NULL,
    valeur_seuil DECIMAL(18,8) NOT NULL,
    statut VARCHAR(20) DEFAULT 'active',
    date_creation TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    date_derniere_notification TIMESTAMPTZ
);
```

### 2.2 Index

```sql
-- Index pour les recherches temporelles
CREATE INDEX idx_prix_bitcoin_timestamp ON prix_bitcoin(timestamp);
CREATE INDEX idx_prediction_timestamp ON prediction(timestamp);
CREATE INDEX idx_indicateur_timestamp ON indicateur_technique(timestamp);

-- Index pour les jointures
CREATE INDEX idx_prediction_modele ON prediction(id_modele);
CREATE INDEX idx_indicateur_prix ON indicateur_technique(id_prix);
CREATE INDEX idx_alerte_utilisateur ON alerte(id_utilisateur);

-- Index pour les recherches fréquentes
CREATE INDEX idx_utilisateur_email ON utilisateur(email);
CREATE INDEX idx_alerte_type_statut ON alerte(type, statut);
```

### 2.3 Partitionnement

```sql
-- Partitionnement des prix par mois
CREATE TABLE prix_bitcoin (
    id BIGSERIAL,
    timestamp TIMESTAMPTZ NOT NULL,
    prix_usd DECIMAL(18,8) NOT NULL,
    volume_24h DECIMAL(24,8),
    market_cap DECIMAL(24,8),
    variation_24h DECIMAL(8,4)
) PARTITION BY RANGE (timestamp);

-- Création des partitions
CREATE TABLE prix_bitcoin_y2024m01 PARTITION OF prix_bitcoin
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
CREATE TABLE prix_bitcoin_y2024m02 PARTITION OF prix_bitcoin
    FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');
-- etc.
```

## 3. Considérations RGPD

### 3.1 Données Personnelles
- Email utilisateur : Nécessaire pour les notifications
- Hash mot de passe : Stocké de manière sécurisée
- Préférences : Stockées en JSON, facilement exportables

### 3.2 Rétention des Données
- Données de prix : Conservation illimitée (données publiques)
- Données utilisateur : Suppression sur demande
- Prédictions : Conservation 1 an
- Alertes : Conservation 6 mois après désactivation

### 3.3 Sécurité
- Chiffrement des données sensibles
- Journalisation des accès
- Sauvegarde quotidienne
- Anonymisation des données de test 