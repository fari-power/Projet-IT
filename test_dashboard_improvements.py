#!/usr/bin/env python3
"""
Script de test pour vérifier les améliorations du Dashboard
"""
import pandas as pd
import sys

def test_improvements():
    """Teste que toutes les améliorations sont en place"""
    
    print("🧪 Test des améliorations du Dashboard\n")
    
    # Test 1: Vérifier l'import des dépendances
    print("1️⃣ Test des imports...")
    try:
        import streamlit as st
        import plotly.express as px
        import plotly.graph_objects as go
        print("   ✅ Streamlit et Plotly importés avec succès")
    except ImportError as e:
        print(f"   ❌ Erreur d'import: {e}")
        return False
    
    # Test 2: Vérifier la structure du fichier streamlit_platform.py
    print("\n2️⃣ Test de la structure du code...")
    with open('streamlit_platform.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = [
        ("Dashboard amélioré", "Top 10 Zones"),
        ("Explorateur avec recherche", "🔍 Rechercher"),
        ("Export CSV", "📥 Exporter CSV"),
        ("Carte interactive", "scatter_mapbox"),
        ("Coloration dynamique", "🎨 Coloration"),
        ("Statistiques détaillées", "Densité moyenne"),
        ("Pivot table", "pd.crosstab"),
    ]
    
    all_ok = True
    for name, pattern in checks:
        if pattern in content:
            print(f"   ✅ {name}")
        else:
            print(f"   ❌ {name} - Pattern '{pattern}' non trouvé")
            all_ok = False
    
    # Test 3: Vérifier la présence des données de test
    print("\n3️⃣ Test des données...")
    try:
        df = pd.read_csv('data/points_vente_casablanca_complet.csv', encoding='utf-8-sig')
        print(f"   ✅ Fichier Casablanca chargé: {len(df)} entrées")
        
        # Vérifier les colonnes essentielles
        required_cols = ['Latitude', 'Longitude', 'Nom', 'Catégorie', 'Statut', 'Zone']
        missing = [col for col in required_cols if col not in df.columns]
        if missing:
            print(f"   ⚠️ Colonnes manquantes: {missing}")
        else:
            print(f"   ✅ Toutes les colonnes essentielles présentes")
    except FileNotFoundError:
        print("   ⚠️ Pas de données Casablanca (normal si pas encore scrapé)")
    except Exception as e:
        print(f"   ❌ Erreur de lecture: {e}")
    
    # Test 4: Vérifier les améliorations spécifiques
    print("\n4️⃣ Test des fonctionnalités spécifiques...")
    
    # Dashboard
    has_top10_zones = "Top 10 Zones" in content and "orientation='h'" in content
    print(f"   {'✅' if has_top10_zones else '❌'} Dashboard: Top 10 Zones (horizontal)")
    
    # Explorateur
    has_search = "st.text_input" in content and "🔍 Rechercher" in content
    has_export = "st.download_button" in content and "export_" in content
    print(f"   {'✅' if has_search else '❌'} Explorateur: Barre de recherche")
    print(f"   {'✅' if has_export else '❌'} Explorateur: Export CSV")
    
    # Carte
    has_plotly_map = "px.scatter_mapbox" in content
    has_color_options = "🎨 Coloration" in content and "Catégorie" in content
    print(f"   {'✅' if has_plotly_map else '❌'} Carte: Plotly scatter_mapbox")
    print(f"   {'✅' if has_color_options else '❌'} Carte: Options de coloration")
    
    # Test 5: Résumé final
    print("\n" + "="*50)
    if all_ok:
        print("✅ TOUS LES TESTS RÉUSSIS!")
        print("\n📝 Prochaines étapes:")
        print("1. Lancer l'application: streamlit run streamlit_platform.py")
        print("2. Se connecter (admin / morocco2024)")
        print("3. Tester les 3 sections: Dashboard, Explorateur, Carte")
        print("4. Si pas de données, lancer un scraping dans le Labo")
        return True
    else:
        print("⚠️ Certains tests ont échoué (voir détails ci-dessus)")
        return False

if __name__ == "__main__":
    success = test_improvements()
    sys.exit(0 if success else 1)
