#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test rapide du scraping pour comparer avec Streamlit
"""

import time
from scraping_orchestrator import ScrapingOrchestrator

def test_scraping_casablanca():
    """Test de scraping simple de Casablanca"""
    print("="*80)
    print("🧪 TEST SCRAPING RAPIDE - CASABLANCA")
    print("="*80)
    
    # Callbacks pour voir la progression
    def progress_callback(current, total, message):
        print(f"⏳ [{current}/{total}] {message}")
    
    def log_callback(message, level):
        print(f"[{level}] {message}")
    
    # Orchestrateur
    orchestrator = ScrapingOrchestrator(verbose=True)
    orchestrator.set_progress_callback(progress_callback)
    orchestrator.set_log_callback(log_callback)
    
    # Lancer le scraping
    print("\n🚀 Démarrage du scraping...")
    start_time = time.time()
    
    summary = orchestrator.scrape_multiple_zones(
        zones=["Ville: Casablanca"],
        duplicate_strategy='keep_best'
    )
    
    elapsed = time.time() - start_time
    
    # Résultats
    print("\n" + "="*80)
    print("📊 RÉSULTATS")
    print("="*80)
    print(f"✅ Zones réussies   : {summary['success_count']}")
    print(f"📊 Points collectés : {summary['total_points']}")
    print(f"❌ Erreurs          : {summary['error_count']}")
    print(f"⏱️  Durée           : {elapsed:.1f}s")
    print("="*80)
    
    # Fichier généré
    import os
    csv_file = "data/points_vente_casablanca_complet.csv"
    if os.path.exists(csv_file):
        size = os.path.getsize(csv_file) / 1024
        print(f"\n📄 Fichier généré: {csv_file} ({size:.1f} KB)")
    
    return summary

if __name__ == "__main__":
    test_scraping_casablanca()
