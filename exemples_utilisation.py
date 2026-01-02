"""
Exemples d'utilisation du système de scraping
Lancez ces exemples pour comprendre comment utiliser le système
"""

import sys
sys.path.append('.')

print("=" * 80)
print("📚 EXEMPLES D'UTILISATION - Système de Scraping")
print("=" * 80)

# ============================================================================
# EXEMPLE 1 : Lister les zones disponibles
# ============================================================================

print("\n" + "=" * 80)
print("EXEMPLE 1 : Lister toutes les zones disponibles")
print("=" * 80)

from morocco_zones_config import REGIONS, CITIES, get_all_zones

print(f"\n📍 Régions disponibles ({len(REGIONS)}) :")
for i, region_name in enumerate(REGIONS.keys(), 1):
    print(f"   {i}. {region_name}")

print(f"\n🏙️  Villes disponibles ({len(CITIES)}) :")
for i, city_name in enumerate(list(CITIES.keys())[:10], 1):
    print(f"   {i}. {city_name}")
print(f"   ... et {len(CITIES) - 10} autres")

# ============================================================================
# EXEMPLE 2 : Scraper une seule ville (simulation)
# ============================================================================

print("\n" + "=" * 80)
print("EXEMPLE 2 : Scraper une ville (simulation)")
print("=" * 80)

print("""
Pour scraper Casablanca :

from scraping_orchestrator import quick_scrape_zone

result = quick_scrape_zone("Ville: Casablanca")

if result['status'] == 'success':
    print(f"✅ Succès : {result['count']} points collectés")
    print(f"⏱️  Durée : {result['duration']:.1f}s")
else:
    print(f"❌ Erreur : {result['error']}")
""")

# ============================================================================
# EXEMPLE 3 : Scraper plusieurs villes
# ============================================================================

print("\n" + "=" * 80)
print("EXEMPLE 3 : Scraper plusieurs villes")
print("=" * 80)

print("""
Pour scraper Casablanca, Rabat et Fès :

from scraping_orchestrator import quick_scrape_cities

summary = quick_scrape_cities(["Casablanca", "Rabat", "Fès"])

print(f"Zones traitées : {summary['success_count']}/{summary['total_zones']}")
print(f"Points collectés : {summary['total_points']}")
print(f"Erreurs : {summary['error_count']}")
print(f"Durée totale : {summary['total_duration']:.1f}s")
""")

# ============================================================================
# EXEMPLE 4 : Utiliser l'orchestrateur avec callbacks
# ============================================================================

print("\n" + "=" * 80)
print("EXEMPLE 4 : Orchestrateur avec callbacks")
print("=" * 80)

print("""
Pour suivre la progression en temps réel :

from scraping_orchestrator import ScrapingOrchestrator

# Créer l'orchestrateur
orchestrator = ScrapingOrchestrator(verbose=True)

# Définir un callback de progression
def show_progress(current, total, message):
    percent = (current / total) * 100
    print(f"[{percent:.1f}%] {message}")

# Définir un callback de log
def show_log(message, level):
    print(f"[{level}] {message}")

# Configurer les callbacks
orchestrator.set_progress_callback(show_progress)
orchestrator.set_log_callback(show_log)

# Lancer le scraping
zones = ["Ville: Casablanca", "Ville: Rabat"]
summary = orchestrator.scrape_multiple_zones(zones)
""")

# ============================================================================
# EXEMPLE 5 : Lire et analyser les données
# ============================================================================

print("\n" + "=" * 80)
print("EXEMPLE 5 : Lire et analyser les données")
print("=" * 80)

print("""
Pour lire les données après scraping :

import pandas as pd

# Charger le CSV
df = pd.read_csv("data/points_vente_casablanca_complet.csv")

# Afficher les infos
print(f"Total de points : {len(df)}")
print(f"\\nRépartition par catégorie :")
print(df['Catégorie'].value_counts())

print(f"\\nRépartition Formel/Informel :")
print(df['Statut'].value_counts())

# Filtrer
supermarchés = df[df['Catégorie'] == 'Supermarché']
print(f"\\nSupermarchés : {len(supermarchés)}")
""")

# ============================================================================
# EXEMPLE 6 : Consulter l'historique
# ============================================================================

print("\n" + "=" * 80)
print("EXEMPLE 6 : Consulter l'historique des mises à jour")
print("=" * 80)

print("""
Pour voir l'historique d'une zone :

from data_manager import DataManager

manager = DataManager("Casablanca")

# Récupérer l'historique
history = manager.get_history()

if history:
    print(f"Zone : {history['zone']}")
    print(f"Créée le : {history['created_at']}")
    print(f"Nombre de mises à jour : {len(history['updates'])}")
    
    # Dernière mise à jour
    last = history['updates'][-1]
    print(f"\\nDernière mise à jour :")
    print(f"  Date : {last['timestamp']}")
    print(f"  Ajoutés : {last['stats']['added']}")
    print(f"  Mis à jour : {last['stats']['updated']}")
    print(f"  Total : {last['stats']['total_after']}")

# Statistiques résumées
stats = manager.get_stats_summary()
print(f"\\nStatistiques actuelles :")
print(f"  Points actuels : {stats['current_count']}")
print(f"  Total mises à jour : {stats['total_updates']}")
""")

# ============================================================================
# EXEMPLE 7 : Scraper tout le Maroc
# ============================================================================

print("\n" + "=" * 80)
print("EXEMPLE 7 : Scraper tout le Maroc")
print("=" * 80)

print("""
Pour scraper toutes les régions du Maroc :

from scraping_orchestrator import ScrapingOrchestrator

orchestrator = ScrapingOrchestrator(verbose=True)

# Option 1 : Toutes les régions
summary = orchestrator.scrape_all_regions()

# Option 2 : Toutes les villes
summary = orchestrator.scrape_all_cities()

# Option 3 : Tout (régions pour éviter doublons)
summary = orchestrator.scrape_all_morocco()

print(f"\\n📊 Résumé final :")
print(f"  Zones réussies : {summary['success_count']}")
print(f"  Zones en erreur : {summary['error_count']}")
print(f"  Points totaux : {summary['total_points']}")
print(f"  Durée : {summary['total_duration']:.1f}s")

# Sauvegarder un rapport
orchestrator.save_results_report("rapport_scraping.csv")
""")

# ============================================================================
# EXEMPLE 8 : Configurer la détection de doublons
# ============================================================================

print("\n" + "=" * 80)
print("EXEMPLE 8 : Configurer la détection de doublons")
print("=" * 80)

print("""
Pour ajuster les seuils de détection :

from duplicate_detection import CONFIG

# Voir la configuration actuelle
print("Configuration actuelle :")
print(f"  Similarité nom : {CONFIG['name_similarity_threshold']}")
print(f"  Distance GPS : {CONFIG['distance_threshold_meters']}m")
print(f"  Score combiné : {CONFIG['combined_score_threshold']}")

# Modifier (dans votre code)
CONFIG['name_similarity_threshold'] = 0.90  # Plus strict
CONFIG['distance_threshold_meters'] = 30    # Rayon plus petit
CONFIG['combined_score_threshold'] = 0.80   # Score plus élevé

# Ou créer une config personnalisée
my_config = {
    'name_similarity_threshold': 0.80,
    'distance_threshold_meters': 100,
    'combined_score_threshold': 0.70
}

# Utiliser avec la fonction
from duplicate_detection import find_duplicates
duplicates = find_duplicates(df, config=my_config)
""")

# ============================================================================
# EXEMPLE 9 : Stratégies de gestion des doublons
# ============================================================================

print("\n" + "=" * 80)
print("EXEMPLE 9 : Stratégies de gestion des doublons")
print("=" * 80)

print("""
Différentes stratégies disponibles :

from scraping_orchestrator import ScrapingOrchestrator

orchestrator = ScrapingOrchestrator()

# Stratégie 1 : Garder la meilleure (plus de données)
summary = orchestrator.scrape_multiple_zones(
    zones=["Ville: Casablanca"],
    duplicate_strategy='keep_best'  # Par défaut
)

# Stratégie 2 : Garder la première occurrence
summary = orchestrator.scrape_multiple_zones(
    zones=["Ville: Casablanca"],
    duplicate_strategy='keep_first'
)

# Stratégie 3 : Priorité aux données OSM
summary = orchestrator.scrape_multiple_zones(
    zones=["Ville: Casablanca"],
    duplicate_strategy='keep_osm'
)

# Stratégie 4 : Priorité aux données ATP
summary = orchestrator.scrape_multiple_zones(
    zones=["Ville: Casablanca"],
    duplicate_strategy='keep_atp'
)
""")

# ============================================================================
# EXEMPLE 10 : Statistiques globales
# ============================================================================

print("\n" + "=" * 80)
print("EXEMPLE 10 : Obtenir les statistiques globales")
print("=" * 80)

print("""
Pour voir les stats de toutes les zones :

from data_manager import get_global_stats, get_all_zones_history

# Stats globales
stats = get_global_stats()
print(f"Zones scrapées : {stats['total_zones']}")
print(f"Points totaux : {stats['total_points']}")
print(f"Mises à jour : {stats['total_updates']}")

# Historique de toutes les zones
all_histories = get_all_zones_history()

print(f"\\nDétail par zone :")
for history in all_histories:
    zone = history['zone']
    updates = len(history['updates'])
    print(f"  {zone} : {updates} mises à jour")
""")

# ============================================================================
# RÉSUMÉ
# ============================================================================

print("\n" + "=" * 80)
print("📝 RÉSUMÉ")
print("=" * 80)

print("""
Cas d'usage principaux :

1. 🎯 Scraping simple d'une ville
   → quick_scrape_zone("Ville: Casablanca")

2. 🎯 Scraping de plusieurs villes
   → quick_scrape_cities(["Casablanca", "Rabat"])

3. 🎯 Scraping avec contrôle total
   → ScrapingOrchestrator() + callbacks

4. 📊 Lecture des données
   → pd.read_csv("data/points_vente_xxx.csv")

5. 📜 Consultation historique
   → DataManager("Zone").get_history()

6. 🌍 Scraping complet Maroc
   → orchestrator.scrape_all_morocco()

💡 Conseil : Utilisez l'interface Streamlit pour débuter !
   streamlit run streamlit_platform.py
""")

print("\n" + "=" * 80)
print("✅ Guide des exemples terminé !")
print("=" * 80)
print("\nPour plus d'informations :")
print("  • QUICK_START.md - Guide de démarrage")
print("  • README_SCRAPING_SYSTEM.md - Documentation complète")
print("  • test_scraping_system.py - Tests automatisés")
