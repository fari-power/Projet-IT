# 🚀 Système de Scraping Industry-Grade - Points de Vente Maroc

## 📋 Vue d'ensemble

Système professionnel de scraping et gestion de données pour les points de vente au Maroc. Inclut :

- ✅ Scraping intelligent OSM avec gestion des doublons
- ✅ Support de toutes les régions et villes du Maroc
- ✅ Détection de doublons industry-grade (fuzzy matching + distance GPS)
- ✅ Versioning et historique complet
- ✅ Interface Streamlit avec suivi en temps réel
- ✅ Backups automatiques

## 📁 Architecture du Projet

```
Projet-IT/
├── 🆕 morocco_zones_config.py          # Configuration zones Maroc
├── 🆕 duplicate_detection.py           # Détection doublons intelligente
├── 🆕 data_manager.py                  # Gestion données + versioning
├── 🆕 osm_scraper_module.py            # Module scraping OSM refactorisé
├── 🆕 scraping_orchestrator.py         # Orchestrateur multi-zones
├── 🔄 streamlit_platform.py            # Interface Streamlit (+ section Labo)
├── osm_complet_scraper.py              # Ancien script (legacy)
├── geocode_utils.py                    # Utilitaires géocodage
│
├── 📁 data/                            # Fichiers CSV des points de vente
├── 📁 logs/                            # Logs de scraping horodatés
├── 📁 backups/                         # Backups automatiques
├── 📁 history/                         # Historique JSON des mises à jour
└── 📁 icons/                           # Icônes des catégories
```

## 🎯 Fonctionnalités Principales

### 1. Configuration des Zones du Maroc

**Fichier:** `morocco_zones_config.py`

- **12 régions administratives** avec leurs bbox
- **27 grandes villes** avec découpage en sous-zones
- Configuration complète et extensible

```python
from morocco_zones_config import get_all_zones, REGIONS, CITIES

# Récupérer toutes les zones
all_zones = get_all_zones()

# Accéder à une région
print(REGIONS["Casablanca-Settat"])

# Accéder à une ville
print(CITIES["Casablanca"])
```

### 2. Détection de Doublons Intelligente

**Fichier:** `duplicate_detection.py`

Utilise 3 méthodes combinées :
- **Fuzzy matching** sur les noms (Levenshtein + SequenceMatcher)
- **Distance GPS** (Haversine - précision métrique)
- **Score combiné** pondéré

```python
from duplicate_detection import find_duplicates, remove_duplicates, merge_with_existing

# Configuration
CONFIG = {
    "name_similarity_threshold": 0.85,   # 85% de similarité
    "distance_threshold_meters": 50,     # 50 mètres
    "combined_score_threshold": 0.75,    # Score minimum
}

# Nettoyer les doublons
df_clean, removed = remove_duplicates(df, strategy='keep_best')

# Fusionner avec données existantes
df_merged, stats = merge_with_existing(new_df, existing_df)
```

### 3. Gestion des Données avec Versioning

**Fichier:** `data_manager.py`

- ✅ Backups automatiques avant chaque modification
- ✅ Historique JSON complet
- ✅ Logs horodatés
- ✅ Fusion intelligente

```python
from data_manager import DataManager

# Créer un gestionnaire
manager = DataManager("Casablanca")

# Ajouter/mettre à jour des données
manager.update_data(new_df, duplicate_strategy='keep_best')

# Récupérer les statistiques
stats = manager.get_stats_summary()

# Récupérer l'historique
history = manager.get_history()
```

### 4. Module de Scraping OSM

**Fichier:** `osm_scraper_module.py`

Module refactorisé avec paramètres dynamiques :

```python
from osm_scraper_module import scrape_zone

# Scraper une zone
df = scrape_zone(
    bbox="33.590,-7.630,33.600,-7.610",
    zone_name="Casablanca Centre-Ville",
    atp_file="points_vente_casablanca_atp.csv"
)
```

### 5. Orchestrateur Multi-Zones

**Fichier:** `scraping_orchestrator.py`

Gère le scraping de plusieurs zones avec progression :

```python
from scraping_orchestrator import ScrapingOrchestrator

# Créer l'orchestrateur
orchestrator = ScrapingOrchestrator(verbose=True)

# Callbacks optionnels
def progress_callback(current, total, message):
    print(f"Progression: {current}/{total} - {message}")

orchestrator.set_progress_callback(progress_callback)

# Scraper plusieurs villes
summary = orchestrator.scrape_multiple_zones([
    "Ville: Casablanca",
    "Ville: Rabat",
    "Ville: Fès"
])

# Scraper tout le Maroc
summary = orchestrator.scrape_all_morocco()
```

## 🖥️ Interface Streamlit - Section "Labo"

### Accès

1. Lancez Streamlit : `streamlit run streamlit_platform.py`
2. Connectez-vous (admin / 123)
3. Allez dans **"🧪 Labo - Scraping"**

### Fonctionnalités

#### Onglet 1: 🚀 Scraping

- **4 modes de scraping** :
  - Sélection personnalisée (régions/villes)
  - Toutes les régions
  - Toutes les villes
  - Tout le Maroc

- **Paramètres avancés** :
  - Stratégie de gestion des doublons
  - Affichage des logs

- **Suivi en temps réel** :
  - Barre de progression
  - Logs détaillés
  - Statistiques finales

#### Onglet 2: 📊 Historique

- Statistiques globales
- Historique par zone
- Détails des mises à jour

#### Onglet 3: ⚙️ Configuration

- Liste des zones disponibles
- Paramètres de scraping
- Structure des fichiers

## 🔧 Installation

### Prérequis

```bash
pip install pandas streamlit requests streamlit-authenticator pyyaml
```

### Structure des Dossiers

Les dossiers sont créés automatiquement :

```bash
mkdir data logs backups history icons
```

## 📖 Guide d'Utilisation

### Scénario 1 : Scraper une seule ville

```python
from scraping_orchestrator import quick_scrape_zone

# Scraper Casablanca
result = quick_scrape_zone("Ville: Casablanca")
print(result)
```

### Scénario 2 : Scraper plusieurs villes

```python
from scraping_orchestrator import quick_scrape_cities

# Scraper plusieurs villes
summary = quick_scrape_cities(["Casablanca", "Rabat", "Fès"])
```

### Scénario 3 : Scraper tout le Maroc

```python
from scraping_orchestrator import ScrapingOrchestrator

orchestrator = ScrapingOrchestrator()
summary = orchestrator.scrape_all_morocco()
```

### Scénario 4 : Utiliser via l'interface Streamlit

1. Lancez `streamlit run streamlit_platform.py`
2. Connectez-vous
3. Allez dans "🧪 Labo - Scraping"
4. Sélectionnez vos zones
5. Cliquez sur "🚀 Lancer le scraping"

## 🎯 Gestion des Doublons - Détails Techniques

### Algorithme de Détection

1. **Normalisation du texte**
   - Conversion en minuscules
   - Suppression accents
   - Tokenisation

2. **Similarité de noms** (Score 0-1)
   - SequenceMatcher (40%)
   - Levenshtein normalisé (40%)
   - Token-based matching (20%)

3. **Distance géographique**
   - Haversine (précision métrique)
   - Score inversé (proche = score élevé)

4. **Score combiné**
   ```
   score = 0.6 * name_similarity + 0.4 * distance_score + 0.05 * category_match + 0.05 * address_similarity
   ```

5. **Décision**
   - Score >= 0.75 → Doublon détecté
   - Stratégie de résolution appliquée

### Stratégies de Résolution

- **`keep_first`** : Garde la première occurrence
- **`keep_best`** : Garde l'entrée la plus complète (plus de champs remplis)
- **`keep_osm`** : Priorité aux données OpenStreetMap
- **`keep_atp`** : Priorité aux données AllThePlaces

## 📊 Format des Données

### Fichiers CSV

Chaque zone a son propre fichier :

```csv
Zone,Nom,Catégorie,Statut,Adresse,Latitude,Longitude,Image,Source
Casablanca,Marjane Anfa,Supermarché,Formel,"Bd Anfa, Casablanca",33.5901,-7.6501,icons/supermarket.png,OSM
```

### Fichiers d'Historique (JSON)

```json
{
  "zone": "Casablanca",
  "created_at": "2026-01-01T12:00:00",
  "updates": [
    {
      "timestamp": "2026-01-01T14:30:00",
      "operation": "merge",
      "stats": {
        "added": 150,
        "updated": 20,
        "ignored": 10,
        "duplicates_removed": 5
      }
    }
  ]
}
```

## 🔍 Tests et Validation

### Test des Modules

```bash
# Test de la configuration
python morocco_zones_config.py

# Test de la détection de doublons
python duplicate_detection.py

# Test du gestionnaire de données
python data_manager.py

# Test du module de scraping
python osm_scraper_module.py

# Test de l'orchestrateur
python scraping_orchestrator.py
```

## 🚨 Gestion des Erreurs

Le système gère automatiquement :

- ✅ Timeouts API
- ✅ Erreurs de connexion
- ✅ Fichiers manquants
- ✅ Données corrompues
- ✅ Permissions fichiers

Tous les logs sont sauvegardés dans `logs/`.

## 📈 Performance

### Temps de Scraping Estimé

- 1 ville : ~30-60 secondes
- 1 région : ~2-5 minutes
- Tout le Maroc : ~30-60 minutes

### Limites API

- Délai entre requêtes : 2 secondes (configurable)
- Timeout : 120 secondes (configurable)
- Retry : 3 tentatives (configurable)

## 🔧 Configuration Avancée

### Modifier les Seuils de Doublons

Dans `duplicate_detection.py` :

```python
CONFIG = {
    "name_similarity_threshold": 0.85,  # Ajuster entre 0-1
    "distance_threshold_meters": 50,     # Ajuster le rayon en mètres
    "combined_score_threshold": 0.75,    # Ajuster le score final
}
```

### Ajouter une Nouvelle Zone

Dans `morocco_zones_config.py` :

```python
CITIES["Nouvelle_Ville"] = {
    "bbox": "lat_min,lon_min,lat_max,lon_max",
    "region": "Nom_Region",
    "population": 100000,
    "zones": [
        {"name": "Zone1", "bbox": "..."},
    ]
}
```

## 📝 Maintenance

### Nettoyage des Backups

```python
from data_manager import cleanup_old_backups

# Supprimer les backups > 30 jours
cleanup_old_backups(days=30)
```

### Statistiques Globales

```python
from data_manager import get_global_stats

stats = get_global_stats()
print(f"Total zones: {stats['total_zones']}")
print(f"Total points: {stats['total_points']}")
```

## 🤝 Contribution

Pour ajouter des fonctionnalités :

1. Testez localement
2. Ajoutez des tests unitaires
3. Mettez à jour la documentation
4. Commitez avec des messages clairs

## 📞 Support

Pour toute question ou problème :

1. Vérifiez les logs dans `logs/`
2. Consultez l'historique dans `history/`
3. Testez les modules individuellement

## 🎉 Fonctionnalités Futures

- [ ] Support de sources de données additionnelles
- [ ] Export vers base de données SQL
- [ ] API REST pour accès externe
- [ ] Dashboard de monitoring avancé
- [ ] Notifications email/Slack
- [ ] Scraping incrémental optimisé

---

**Créé avec ❤️ pour une gestion professionnelle des données de points de vente au Maroc**
