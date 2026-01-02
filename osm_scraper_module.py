"""
Module de scraping OSM refactorisé
Version modulaire avec paramètres dynamiques pour bbox
"""

import pandas as pd
import time
import os
import requests

# --- Icônes ---
os.makedirs("icons", exist_ok=True)
IMAGES = {
    "Supermarché": "icons/supermarket.png",
    "Supérette / Mini-market": "icons/convenience.png",
    "Épicerie": "icons/greengrocer.png",
    "Café": "icons/cafe.png",
    "Restaurant": "icons/restaurant.png",
    "Grossiste / Distributeur régional": "icons/wholesale.png",
    "Kiosque": "icons/kiosk.png",
    "Boulangerie": "icons/bakery.png",
    "Parapharmacie": "icons/pharmacy.png",
    "Boutique de confiserie": "icons/confectionery.png",
    "Magasin bio": "icons/organic.png",
}

def query_overpass_api(query, timeout=120):
    """Effectue une requête vers l'API Overpass d'OpenStreetMap"""
    overpass_url = "https://overpass.kumi.systems/api/interpreter"
    try:
        response = requests.get(overpass_url, params={'data': query}, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"[WARNING] Erreur API Overpass: {e}")
        return None

def build_overpass_query(bbox, timeout=120):
    """
    Construit la requête Overpass pour une bbox donnée
    
    Args:
        bbox: String au format "lat_min,lon_min,lat_max,lon_max"
        timeout: Timeout en secondes
    
    Returns:
        String de requête Overpass
    """
    query = f"""
    [out:json][timeout:{timeout}];
    (
      // Supermarchés et grandes surfaces
      node["shop"="supermarket"]({bbox});
      way["shop"="supermarket"]({bbox});
      relation["shop"="supermarket"]({bbox});
      
      // Magasins de proximité
      node["shop"="convenience"]({bbox});
      way["shop"="convenience"]({bbox});
      relation["shop"="convenience"]({bbox});
      
      // Épiceries
      node["shop"="general"]({bbox});
      way["shop"="general"]({bbox});
      relation["shop"="general"]({bbox});
      
      node["shop"="greengrocer"]({bbox});
      way["shop"="greengrocer"]({bbox});
      relation["shop"="greengrocer"]({bbox});
      
      // Boulangeries
      node["shop"="bakery"]({bbox});
      way["shop"="bakery"]({bbox});
      relation["shop"="bakery"]({bbox});
      
      // Parapharmacies
      node["shop"="chemist"]({bbox});
      way["shop"="chemist"]({bbox});
      relation["shop"="chemist"]({bbox});
      
      // Pharmacies
      node["amenity"="pharmacy"]({bbox});
      way["amenity"="pharmacy"]({bbox});
      relation["amenity"="pharmacy"]({bbox});
      
      // Cafés
      node["amenity"="cafe"]({bbox});
      way["amenity"="cafe"]({bbox});
      relation["amenity"="cafe"]({bbox});
      
      // Restaurants
      node["amenity"="restaurant"]({bbox});
      way["amenity"="restaurant"]({bbox});
      relation["amenity"="restaurant"]({bbox});
      
      // Fast food
      node["amenity"="fast_food"]({bbox});
      way["amenity"="fast_food"]({bbox});
      relation["amenity"="fast_food"]({bbox});
      
      // Kiosques
      node["shop"="kiosk"]({bbox});
      way["shop"="kiosk"]({bbox});
      relation["shop"="kiosk"]({bbox});
      
      // Magasins bio
      node["shop"="organic"]({bbox});
      way["shop"="organic"]({bbox});
      relation["shop"="organic"]({bbox});
      
      // Confiseries
      node["shop"="confectionery"]({bbox});
      way["shop"="confectionery"]({bbox});
      relation["shop"="confectionery"]({bbox});
      
      // Marchés
      node["amenity"="marketplace"]({bbox});
      way["amenity"="marketplace"]({bbox});
      relation["amenity"="marketplace"]({bbox});
    );
    out center;
    """
    return query

def categorize_point(element):
    """Détermine la catégorie et le statut d'un point de vente"""
    
    if 'tags' not in element:
        return None, None
    
    tags = element['tags']
    shop_type = tags.get('shop', '')
    amenity_type = tags.get('amenity', '')
    
    # Mapping des catégories OSM vers nos catégories
    category_mapping = {
        # Formel - Grandes surfaces
        'supermarket': ("Supermarché", "Formel"),
        'convenience': ("Supérette / Mini-market", "Formel"),
        
        # Informel - Commerces traditionnels
        'general': ("Épicerie", "Informel"),
        'greengrocer': ("Épicerie", "Informel"),
        'kiosk': ("Kiosque", "Informel"),
        'confectionery': ("Boutique de confiserie", "Informel"),
        
        # Formel - Services
        'bakery': ("Boulangerie", "Formel"),
        'chemist': ("Parapharmacie", "Formel"),
        'organic': ("Magasin bio", "Formel"),
    }
    
    amenity_mapping = {
        'pharmacy': ("Parapharmacie", "Formel"),
        'cafe': ("Café", "Formel"),
        'restaurant': ("Restaurant", "Formel"),
        'fast_food': ("Restaurant", "Formel"),
        'marketplace': ("Épicerie", "Informel"),
    }
    
    # Déterminer la catégorie
    if shop_type in category_mapping:
        return category_mapping[shop_type]
    elif amenity_type in amenity_mapping:
        return amenity_mapping[amenity_type]
    else:
        # Catégorie par défaut
        return ("Épicerie", "Informel")

def scrape_osm_data(bbox, zone_name=None, verbose=True):
    """
    Scrape les données OSM pour une bbox donnée
    
    Args:
        bbox: String au format "lat_min,lon_min,lat_max,lon_max"
        zone_name: Nom de la zone pour le champ "Zone"
        verbose: Afficher les logs
    
    Returns:
        DataFrame avec les points collectés
    """
    if verbose:
        print(f"[INFO] Scraping OSM pour bbox: {bbox}")
        if zone_name:
            print(f"[INFO] Zone: {zone_name}")
    
    # Construire et exécuter la requête
    query = build_overpass_query(bbox)
    osm_data = query_overpass_api(query)
    
    if not osm_data or 'elements' not in osm_data:
        if verbose:
            print("[ERROR] Aucune donnée OSM collectée")
        return pd.DataFrame()
    
    if verbose:
        print(f"[INFO] {len(osm_data['elements'])} éléments bruts collectés")
    
    # Parser les éléments
    osm_points = []
    for element in osm_data['elements']:
        if 'tags' not in element:
            continue
        
        # Extraire les coordonnées
        if element['type'] == 'node':
            lat = element.get('lat')
            lon = element.get('lon')
        elif element['type'] in ['way', 'relation'] and 'center' in element:
            lat = element['center'].get('lat')
            lon = element['center'].get('lon')
        else:
            continue
        
        if not lat or not lon:
            continue
        
        # Catégoriser
        category_info = categorize_point(element)
        if not category_info[0]:
            continue
        
        category, statut = category_info
        name = element['tags'].get('name', f"{category} sans nom")
        
        # Extraire l'adresse
        address_parts = []
        for addr_key in ['addr:full', 'addr:street', 'addr:city']:
            if addr_key in element['tags']:
                address_parts.append(element['tags'][addr_key])
        address = ', '.join(address_parts) if address_parts else name
        
        # Image
        image = IMAGES.get(category, "icons/supermarket.png")
        
        osm_points.append({
            "Zone": zone_name if zone_name else "Non défini",
            "Nom": name,
            "Catégorie": category,
            "Statut": statut,
            "Adresse": address,
            "Latitude": lat,
            "Longitude": lon,
            "Image": image,
            "Source": "OSM"
        })
    
    df = pd.DataFrame(osm_points)
    
    if verbose:
        print(f"[SUCCESS] {len(df)} points valides extraits")
    
    return df

def scrape_atp_data(atp_file="points_vente_casablanca_atp.csv", zone_name=None, verbose=True):
    """
    Charge les données ATP depuis un fichier CSV
    
    Args:
        atp_file: Chemin du fichier ATP
        zone_name: Nom de la zone pour le champ "Zone"
        verbose: Afficher les logs
    
    Returns:
        DataFrame avec les points ATP
    """
    if not os.path.exists(atp_file):
        if verbose:
            print(f"[INFO] Fichier ATP non trouvé: {atp_file}")
        return pd.DataFrame()
    
    try:
        df_atp = pd.read_csv(atp_file, encoding='utf-8-sig')
        
        # Ajouter la zone si nécessaire
        if zone_name and 'Zone' not in df_atp.columns:
            df_atp['Zone'] = zone_name
        
        # Ajouter la source
        if 'Source' not in df_atp.columns:
            df_atp['Source'] = 'ATP'
        
        if verbose:
            print(f"[SUCCESS] {len(df_atp)} points ATP chargés")
        
        return df_atp
    except Exception as e:
        if verbose:
            print(f"[ERROR] Erreur chargement ATP: {e}")
        return pd.DataFrame()

def scrape_zone(bbox, zone_name=None, atp_file=None, verbose=True):
    """
    Scrape une zone complète (OSM + ATP)
    
    Args:
        bbox: String au format "lat_min,lon_min,lat_max,lon_max"
        zone_name: Nom de la zone
        atp_file: Fichier ATP optionnel
        verbose: Afficher les logs
    
    Returns:
        DataFrame avec tous les points (OSM + ATP)
    """
    if verbose:
        print("=" * 70)
        print(f"SCRAPING DE LA ZONE: {zone_name if zone_name else 'Non définie'}")
        print("=" * 70)
    
    # Scraping OSM
    df_osm = scrape_osm_data(bbox, zone_name, verbose)
    
    # Scraping ATP
    df_atp = pd.DataFrame()
    if atp_file:
        df_atp = scrape_atp_data(atp_file, zone_name, verbose)
    
    # Fusion
    if df_osm.empty and df_atp.empty:
        if verbose:
            print("[ERROR] Aucune donnée collectée")
        return pd.DataFrame()
    
    df_combined = pd.concat([df_osm, df_atp], ignore_index=True)
    
    if verbose:
        print(f"\n[INFO] Total combiné: {len(df_combined)} points")
        print(f"   - OSM: {len(df_osm)}")
        print(f"   - ATP: {len(df_atp)}")
    
    return df_combined

# ============================================================================
# TESTS
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("TEST DU MODULE DE SCRAPING OSM")
    print("=" * 80)
    
    # Test sur une petite zone de Casablanca
    test_bbox = "33.590,-7.630,33.600,-7.610"
    
    df = scrape_zone(test_bbox, zone_name="Casablanca Centre-Ville Test", verbose=True)
    
    if not df.empty:
        print("\n📊 Aperçu des données:")
        print(df.head())
        
        print("\n📊 Statistiques:")
        print(df['Catégorie'].value_counts())
    
    print("\n✅ Test terminé!")
