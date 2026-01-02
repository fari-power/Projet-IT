"""
Orchestrateur de scraping multi-zones
Gère le scraping de plusieurs zones avec suivi de progression
"""

import time
from datetime import datetime
from pathlib import Path
import pandas as pd
from typing import List, Dict, Callable

from morocco_zones_config import get_all_zones, REGIONS, CITIES, SCRAPING_CONFIG
from osm_scraper_module import scrape_zone
from data_manager import DataManager

# ============================================================================
# CLASSE PRINCIPALE
# ============================================================================

class ScrapingOrchestrator:
    """Orchestrateur de scraping multi-zones"""
    
    def __init__(self, verbose=True):
        """
        Initialise l'orchestrateur
        
        Args:
            verbose: Afficher les logs détaillés
        """
        self.verbose = verbose
        self.results = []
        self.errors = []
        self.start_time = None
        self.progress_callback = None
        self.log_callback = None
    
    def set_progress_callback(self, callback: Callable[[int, int, str], None]):
        """
        Définit une callback pour le suivi de progression
        
        Args:
            callback: Fonction(current, total, message) appelée à chaque progression
        """
        self.progress_callback = callback
    
    def set_log_callback(self, callback: Callable[[str, str], None]):
        """
        Définit une callback pour les logs
        
        Args:
            callback: Fonction(message, level) appelée pour chaque log
        """
        self.log_callback = callback
    
    def _log(self, message, level="INFO"):
        """Log un message"""
        if self.verbose:
            print(f"[{level}] {message}")
        
        if self.log_callback:
            self.log_callback(message, level)
    
    def _update_progress(self, current, total, message):
        """Met à jour la progression"""
        if self.progress_callback:
            self.progress_callback(current, total, message)
    
    def scrape_single_zone(self, zone_name, zone_data, duplicate_strategy='keep_best', skip_duplicates=False):
        """
        Scrape une seule zone
        
        Args:
            zone_name: Nom de la zone
            zone_data: Données de configuration de la zone
            duplicate_strategy: Stratégie de gestion des doublons
            skip_duplicates: Si True, skip complètement la détection de doublons (mode rapide)
        
        Returns:
            Dict avec les résultats
        """
        start_time = time.time()
        
        try:
            self._log(f"🚀 Début du scraping: {zone_name}")
            
            if skip_duplicates:
                self._log(f"⚡ Mode rapide activé (sans détection de doublons)")
            
            # Scraping
            df = scrape_zone(
                bbox=zone_data['bbox'],
                zone_name=zone_data['name'],
                verbose=self.verbose
            )
            
            if df.empty:
                self._log(f"⚠️  Aucune donnée pour {zone_name}", "WARNING")
                return {
                    'zone': zone_name,
                    'status': 'no_data',
                    'count': 0,
                    'duration': time.time() - start_time,
                    'error': None
                }
            
            # Sauvegarde avec DataManager
            data_manager = DataManager(zone_data['name'], verbose=self.verbose)
            
            # Mode rapide : passer skip_duplicates au data_manager
            if skip_duplicates:
                success = data_manager.update_data(df, duplicate_strategy, skip_duplicate_detection=True)
            else:
                success = data_manager.update_data(df, duplicate_strategy)
            
            duration = time.time() - start_time
            
            if success:
                stats = data_manager.get_stats_summary()
                self._log(f"✅ {zone_name}: {stats['current_count']} points en {duration:.1f}s")
                
                return {
                    'zone': zone_name,
                    'status': 'success',
                    'count': stats['current_count'],
                    'stats': stats,
                    'duration': duration,
                    'error': None
                }
            else:
                self._log(f"❌ Erreur sauvegarde: {zone_name}", "ERROR")
                return {
                    'zone': zone_name,
                    'status': 'error',
                    'count': len(df),
                    'duration': duration,
                    'error': 'Erreur de sauvegarde'
                }
        
        except Exception as e:
            duration = time.time() - start_time
            self._log(f"❌ Erreur {zone_name}: {e}", "ERROR")
            
            return {
                'zone': zone_name,
                'status': 'error',
                'count': 0,
                'duration': duration,
                'error': str(e)
            }
    
    def scrape_multiple_zones(self, zones: List[str], duplicate_strategy='keep_best', skip_duplicates=False):
        """
        Scrape plusieurs zones
        
        Args:
            zones: Liste des noms de zones à scraper
            duplicate_strategy: Stratégie de gestion des doublons
            skip_duplicates: Si True, mode rapide sans détection de doublons
        
        Returns:
            Dict avec les résultats globaux
        """
        self.start_time = time.time()
        self.results = []
        self.errors = []
        
        all_zones = get_all_zones()
        total_zones = len(zones)
        
        self._log("=" * 80)
        self._log(f"🚀 DÉBUT DU SCRAPING DE {total_zones} ZONES")
        if skip_duplicates:
            self._log(f"⚡ MODE RAPIDE ACTIVÉ (sans détection de doublons)")
        self._log("=" * 80)
        
        for i, zone_key in enumerate(zones, 1):
            # Mise à jour progression
            self._update_progress(i - 1, total_zones, f"Scraping {zone_key}...")
            
            # Récupérer les données de la zone
            zone_data = all_zones.get(zone_key)
            if not zone_data:
                self._log(f"⚠️  Zone inconnue: {zone_key}", "WARNING")
                continue
            
            # Scraper la zone
            result = self.scrape_single_zone(zone_key, zone_data, duplicate_strategy, skip_duplicates)
            self.results.append(result)
            
            if result['status'] == 'error':
                self.errors.append(result)
            
            # Délai pour éviter le throttling
            if i < total_zones:
                delay = SCRAPING_CONFIG['rate_limit_delay']
                self._log(f"⏳ Pause de {delay}s...")
                time.sleep(delay)
        
        # Mise à jour progression finale
        self._update_progress(total_zones, total_zones, "Scraping terminé!")
        
        # Statistiques finales
        total_duration = time.time() - self.start_time
        success_count = sum(1 for r in self.results if r['status'] == 'success')
        total_points = sum(r['count'] for r in self.results if r['status'] == 'success')
        
        summary = {
            'total_zones': total_zones,
            'success_count': success_count,
            'error_count': len(self.errors),
            'total_points': total_points,
            'total_duration': total_duration,
            'results': self.results,
            'errors': self.errors
        }
        
        self._log("=" * 80)
        self._log("📊 RÉSUMÉ DU SCRAPING")
        self._log("=" * 80)
        self._log(f"✅ Zones réussies: {success_count}/{total_zones}")
        self._log(f"❌ Zones en erreur: {len(self.errors)}")
        self._log(f"📍 Points totaux: {total_points}")
        self._log(f"⏱️  Durée totale: {total_duration:.1f}s")
        self._log("=" * 80)
        
        return summary
    
    def scrape_all_regions(self, duplicate_strategy='keep_best'):
        """Scrape toutes les régions du Maroc"""
        zone_keys = [f"Région: {name}" for name in REGIONS.keys()]
        return self.scrape_multiple_zones(zone_keys, duplicate_strategy)
    
    def scrape_all_cities(self, duplicate_strategy='keep_best'):
        """Scrape toutes les villes du Maroc"""
        zone_keys = [f"Ville: {name}" for name in CITIES.keys()]
        return self.scrape_multiple_zones(zone_keys, duplicate_strategy)
    
    def scrape_all_morocco(self, duplicate_strategy='keep_best'):
        """Scrape toutes les zones du Maroc (régions + villes)"""
        all_zones = get_all_zones()
        # Filtrer pour éviter les doublons (scraper seulement régions OU villes)
        # On prend les régions car elles couvrent tout
        zone_keys = [k for k in all_zones.keys() if k.startswith("Région:")]
        return self.scrape_multiple_zones(zone_keys, duplicate_strategy)
    
    def scrape_by_type(self, zone_type='region', duplicate_strategy='keep_best'):
        """
        Scrape par type de zone
        
        Args:
            zone_type: 'region', 'city', ou 'all'
            duplicate_strategy: Stratégie de gestion des doublons
        """
        all_zones = get_all_zones()
        
        if zone_type == 'region':
            zone_keys = [k for k in all_zones.keys() if k.startswith("Région:")]
        elif zone_type == 'city':
            zone_keys = [k for k in all_zones.keys() if k.startswith("Ville:")]
        elif zone_type == 'all':
            zone_keys = list(all_zones.keys())
        else:
            self._log(f"❌ Type de zone inconnu: {zone_type}", "ERROR")
            return None
        
        return self.scrape_multiple_zones(zone_keys, duplicate_strategy)
    
    def get_results_dataframe(self):
        """Retourne les résultats sous forme de DataFrame"""
        if not self.results:
            return pd.DataFrame()
        
        df = pd.DataFrame(self.results)
        return df
    
    def save_results_report(self, output_file="scraping_report.csv"):
        """Sauvegarde un rapport des résultats"""
        df = self.get_results_dataframe()
        if df.empty:
            self._log("⚠️  Aucun résultat à sauvegarder", "WARNING")
            return False
        
        try:
            df.to_csv(output_file, index=False, encoding='utf-8-sig')
            self._log(f"💾 Rapport sauvegardé: {output_file}")
            return True
        except Exception as e:
            self._log(f"❌ Erreur sauvegarde rapport: {e}", "ERROR")
            return False

# ============================================================================
# FONCTIONS UTILITAIRES
# ============================================================================

def quick_scrape_zone(zone_name):
    """
    Fonction rapide pour scraper une zone unique
    
    Args:
        zone_name: Nom complet de la zone (ex: "Ville: Casablanca")
    
    Returns:
        Résultat du scraping
    """
    orchestrator = ScrapingOrchestrator(verbose=True)
    all_zones = get_all_zones()
    
    zone_data = all_zones.get(zone_name)
    if not zone_data:
        print(f"❌ Zone inconnue: {zone_name}")
        return None
    
    return orchestrator.scrape_single_zone(zone_name, zone_data)

def quick_scrape_cities(city_names: List[str]):
    """
    Fonction rapide pour scraper plusieurs villes
    
    Args:
        city_names: Liste de noms de villes (ex: ["Casablanca", "Rabat"])
    
    Returns:
        Résultats du scraping
    """
    orchestrator = ScrapingOrchestrator(verbose=True)
    zone_keys = [f"Ville: {name}" for name in city_names]
    return orchestrator.scrape_multiple_zones(zone_keys)

# ============================================================================
# TESTS
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("TEST DE L'ORCHESTRATEUR DE SCRAPING")
    print("=" * 80)
    
    # Test sur une seule zone
    print("\n🧪 Test 1: Scraping d'une seule ville")
    result = quick_scrape_zone("Ville: Casablanca")
    if result:
        print(f"\n📊 Résultat: {result}")
    
    # Test sur plusieurs villes
    print("\n🧪 Test 2: Scraping de plusieurs villes")
    orchestrator = ScrapingOrchestrator(verbose=True)
    summary = quick_scrape_cities(["Casablanca", "Rabat"])
    
    if summary:
        print(f"\n📊 Résumé:")
        print(f"   Zones: {summary['success_count']}/{summary['total_zones']}")
        print(f"   Points: {summary['total_points']}")
        print(f"   Durée: {summary['total_duration']:.1f}s")
    
    print("\n✅ Tests terminés!")
