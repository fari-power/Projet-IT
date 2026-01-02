# 🚀 Guide de Démarrage Rapide

## 📦 Installation (5 minutes)

### 1. Installer les dépendances

```bash
cd c:\laragon\www\Projet-IT
pip install -r requirements.txt
```

### 2. Tester le système

```bash
python test_scraping_system.py
```

Vous devriez voir :
```
✅ TOUS LES TESTS RÉUSSIS!
```

## 🎯 Utilisation

### Option 1 : Interface Streamlit (Recommandé)

```bash
streamlit run streamlit_platform.py
```

1. **Connexion** : `admin` / `123`
2. **Navigation** : Cliquez sur "🧪 Labo - Scraping"
3. **Sélection** : Choisissez vos zones (régions/villes)
4. **Lancement** : Cliquez sur "🚀 Lancer le scraping"
5. **Suivi** : Regardez la progression en temps réel

### Option 2 : Scripts Python

#### Scraper une ville

```python
from scraping_orchestrator import quick_scrape_zone

# Scraper Casablanca
result = quick_scrape_zone("Ville: Casablanca")
```

#### Scraper plusieurs villes

```python
from scraping_orchestrator import quick_scrape_cities

# Scraper 3 villes
summary = quick_scrape_cities(["Casablanca", "Rabat", "Fès"])

print(f"Points collectés: {summary['total_points']}")
print(f"Durée: {summary['total_duration']:.1f}s")
```

#### Scraper tout le Maroc

```python
from scraping_orchestrator import ScrapingOrchestrator

orchestrator = ScrapingOrchestrator(verbose=True)
summary = orchestrator.scrape_all_morocco()
```

## 📊 Fichiers Générés

Après scraping, vous trouverez :

```
📁 data/
   └── points_vente_casablanca_complet.csv
   └── points_vente_rabat_complet.csv
   └── ...

📁 logs/
   └── casablanca_20260101_143000.log
   └── ...

📁 backups/
   └── points_vente_casablanca_complet_20260101_143000.csv
   └── ...

📁 history/
   └── casablanca_history.json
   └── ...
```

## 🔍 Exemples d'Usage

### 1. Scraper uniquement les régions

```python
from scraping_orchestrator import ScrapingOrchestrator

orchestrator = ScrapingOrchestrator()
summary = orchestrator.scrape_all_regions()
```

### 2. Scraper avec stratégie de doublons personnalisée

```python
from scraping_orchestrator import ScrapingOrchestrator

orchestrator = ScrapingOrchestrator()
summary = orchestrator.scrape_multiple_zones(
    ["Ville: Casablanca", "Ville: Rabat"],
    duplicate_strategy='keep_osm'  # Priorité OSM
)
```

### 3. Lire les données scrapées

```python
import pandas as pd

df = pd.read_csv("data/points_vente_casablanca_complet.csv")
print(f"Points de vente: {len(df)}")
print(df.head())
```

### 4. Analyser l'historique

```python
from data_manager import DataManager

manager = DataManager("Casablanca")
history = manager.get_history()
stats = manager.get_stats_summary()

print(f"Total de mises à jour: {stats['total_updates']}")
print(f"Points actuels: {stats['current_count']}")
```

## ⚙️ Configuration

### Ajuster les seuils de doublons

Éditez `duplicate_detection.py` :

```python
CONFIG = {
    "name_similarity_threshold": 0.85,   # Plus bas = plus de doublons détectés
    "distance_threshold_meters": 50,     # Plus grand = rayon de détection plus large
    "combined_score_threshold": 0.75,    # Score minimum pour doublon
}
```

### Ajouter une nouvelle ville

Éditez `morocco_zones_config.py` :

```python
CITIES["Ma_Ville"] = {
    "bbox": "lat_min,lon_min,lat_max,lon_max",
    "region": "Nom_Region",
    "population": 100000,
    "zones": []
}
```

## 🐛 Dépannage

### Problème : "ModuleNotFoundError"

```bash
pip install -r requirements.txt
```

### Problème : "Permission denied" lors de la sauvegarde

- Fermez le fichier CSV s'il est ouvert dans Excel
- Le système créera un fichier avec timestamp

### Problème : Timeout API Overpass

- Augmentez le timeout dans `morocco_zones_config.py`
- Réduisez la taille de la bbox
- Réessayez plus tard (charge serveur)

### Problème : Peu de résultats

- Vérifiez la bbox (coordonnées correctes ?)
- Vérifiez votre connexion internet
- OSM peut avoir peu de données dans certaines zones

## 📈 Performance

### Temps estimés

- 1 ville : 30-60 secondes
- 1 région : 2-5 minutes
- Tout le Maroc : 30-60 minutes

### Optimisation

- Scraper en heures creuses (moins de charge serveur)
- Utiliser des zones plus petites pour plus de précision
- Vérifier `SCRAPING_CONFIG` dans `morocco_zones_config.py`

## 📚 Documentation Complète

Voir [README_SCRAPING_SYSTEM.md](README_SCRAPING_SYSTEM.md) pour :
- Architecture détaillée
- Documentation API complète
- Cas d'usage avancés
- Maintenance et administration

## 🎓 Tutoriel Complet (15 minutes)

### 1. Premier scraping

```bash
# Test sur Casablanca
python -c "from scraping_orchestrator import quick_scrape_zone; quick_scrape_zone('Ville: Casablanca')"
```

### 2. Vérifier les résultats

```python
import pandas as pd
df = pd.read_csv("data/points_vente_casablanca_complet.csv")
print(df.info())
print(df['Catégorie'].value_counts())
```

### 3. Relancer pour tester la mise à jour

```bash
# Relancer le même scraping
python -c "from scraping_orchestrator import quick_scrape_zone; quick_scrape_zone('Ville: Casablanca')"
```

Le système va :
- ✅ Charger les données existantes
- ✅ Détecter les doublons
- ✅ Ajouter uniquement les nouveaux points
- ✅ Créer une backup
- ✅ Logger les changements

### 4. Vérifier l'historique

```python
from data_manager import DataManager

manager = DataManager("Casablanca")
history = manager.get_history()

print(f"Nombre de mises à jour: {len(history['updates'])}")
for update in history['updates']:
    print(f"  - {update['timestamp']}: {update['stats']['added']} ajoutés")
```

## 🎉 C'est Prêt !

Vous êtes maintenant prêt à :
- ✅ Scraper tout le Maroc
- ✅ Gérer intelligemment les doublons
- ✅ Suivre l'historique complet
- ✅ Utiliser l'interface Streamlit

**Bon scraping ! 🚀**
