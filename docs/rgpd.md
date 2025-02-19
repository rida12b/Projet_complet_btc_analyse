# Documentation RGPD - Bitcoin Trends

## 1. Registre des Traitements

### 1.1 Finalités des Traitements
1. **Gestion des utilisateurs**
   - Création et gestion des comptes
   - Authentification et sécurité
   - Personnalisation des préférences

2. **Service de prédiction**
   - Analyse des données de marché
   - Génération de prédictions
   - Historique des consultations

3. **Système d'alertes**
   - Configuration des alertes
   - Envoi de notifications
   - Suivi des préférences

### 1.2 Bases Légales
- Consentement explicite de l'utilisateur
- Exécution du contrat de service
- Intérêt légitime pour l'amélioration du service

## 2. Données Collectées

### 2.1 Données Personnelles
| Donnée | Finalité | Base légale | Durée de conservation |
|--------|----------|-------------|----------------------|
| Email | Authentification, Notifications | Consentement | Durée du compte |
| Mot de passe (hashé) | Sécurité | Contrat | Durée du compte |
| Préférences | Personnalisation | Consentement | Durée du compte |
| Historique des alertes | Service d'alertes | Consentement | 6 mois |

### 2.2 Données Non Personnelles
- Prix du Bitcoin (public)
- Volumes d'échange (public)
- Indicateurs techniques (calculés)
- Prédictions (générées)

## 3. Mesures Techniques

### 3.1 Sécurité des Données
- Chiffrement TLS en transit
- Hachage des mots de passe (Argon2)
- Cloisonnement des données
- Audit logs

### 3.2 Accès aux Données
- Authentification forte
- Sessions limitées
- Journalisation des accès
- Principe du moindre privilège

### 3.3 Sauvegarde et Restauration
- Backup chiffré quotidien
- Rétention 30 jours
- Test de restauration mensuel
- Procédure documentée

## 4. Droits des Utilisateurs

### 4.1 Information
- Politique de confidentialité claire
- Conditions d'utilisation
- Mentions légales
- Cookie policy

### 4.2 Exercice des Droits
1. **Droit d'accès**
   - Export des données personnelles
   - Visualisation des préférences
   - Historique des utilisations

2. **Droit de rectification**
   - Modification du profil
   - Mise à jour des préférences
   - Correction des informations

3. **Droit à l'effacement**
   - Suppression du compte
   - Effacement des données
   - Conservation minimale

4. **Droit à la portabilité**
   - Export format standard
   - Documentation format
   - Procédure automatisée

## 5. Procédures

### 5.1 Création de Compte
1. Collecte minimale d'informations
2. Consentement explicite
3. Information claire
4. Confirmation email

### 5.2 Suppression de Compte
1. Demande de confirmation
2. Export des données
3. Suppression complète
4. Confirmation email

### 5.3 Violation de Données
1. Détection et évaluation
2. Notification CNIL (72h)
3. Information utilisateurs
4. Mesures correctives

## 6. Documentation Technique

### 6.1 Stockage Sécurisé
```sql
-- Table utilisateur avec données minimales
CREATE TABLE utilisateur (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hash_mot_de_passe VARCHAR(255) NOT NULL,
    date_inscription TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    preferences_notification JSONB,
    derniere_connexion TIMESTAMPTZ,
    statut VARCHAR(20) DEFAULT 'actif'
);

-- Table de consentements
CREATE TABLE consentement (
    id SERIAL PRIMARY KEY,
    id_utilisateur INTEGER REFERENCES utilisateur(id),
    type_consentement VARCHAR(50) NOT NULL,
    date_consentement TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    valeur BOOLEAN NOT NULL
);

-- Table d'audit
CREATE TABLE audit_log (
    id SERIAL PRIMARY KEY,
    date_action TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    type_action VARCHAR(50) NOT NULL,
    id_utilisateur INTEGER,
    details JSONB
);
```

### 6.2 Anonymisation
```python
def anonymize_data(user_id):
    """Anonymisation des données utilisateur"""
    update_user = """
        UPDATE utilisateur
        SET email = 'anonymized_' || id || '@deleted',
            hash_mot_de_passe = NULL,
            preferences_notification = NULL
        WHERE id = %s
    """
    delete_personal_data = """
        DELETE FROM alerte WHERE id_utilisateur = %s;
        DELETE FROM consentement WHERE id_utilisateur = %s;
    """
    # Exécution des requêtes...
```

## 7. Contrôles Réguliers

### 7.1 Audit Interne
- Revue trimestrielle
- Test des procédures
- Vérification logs
- Mise à jour documentation

### 7.2 Maintenance
- Mise à jour sécurité
- Revue des accès
- Test restauration
- Archivage 