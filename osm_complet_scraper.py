import pandas as pd
import time
import os
import requests
from geocode_utils import get_zone

# --- Icônes ---
os.makedirs("icons", exist_ok=True)
images = {
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

def query_overpass_api(query):
    """Effectue une requête vers l'API Overpass d'OpenStreetMap"""
    overpass_url = "https://overpass.kumi.systems/api/interpreter"
    try:
        response = requests.get(overpass_url, params={'data': query}, timeout=60)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"[WARNING] Erreur API Overpass: {e}")
        return None

def get_all_food_retail_casablanca():
    """Recherche TOUS les commerces alimentaires dans la région de Casablanca"""
    
    # Bounding box élargie pour couvrir Marrakech
    # Sud-Ouest: 31.53, -8.10 | Nord-Est: 31.70, -7.90
    bbox = "31.53,-8.10,31.70,-7.90"
    
    print(f"[INFO] Recherche dans la zone: {bbox}")
    
    # Requête pour tous les types de commerces alimentaires
    query = f"""
    [out:json][timeout:120];
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
    
    return query_overpass_api(query)

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

def main():
    """Fonction principale"""
    
    print("="*70)
    print("COLLECTE COMPLETE DES POINTS DE VENTE - CASABLANCA")
    print("="*70)
    
    print("[INFO] Debut de la collecte OSM pour toute la region de Casablanca...")
    
    # --- Collecte OSM ---
    osm_data = get_all_food_retail_casablanca()
    if not osm_data or 'elements' not in osm_data:
        print("[ERROR] Aucune donnee OSM collectee")
        osm_points = []
    else:
        print(f"[INFO] {len(osm_data['elements'])} elements bruts collectes")
        osm_points = []
        for element in osm_data['elements']:
            if 'tags' not in element:
                continue
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
            category_info = categorize_point(element)
            if not category_info[0]:
                continue
            category, statut = category_info
            name = element['tags'].get('name', f"{category} sans nom")
            address_parts = []
            for addr_key in ['addr:full', 'addr:street', 'addr:city']:
                if addr_key in element['tags']:
                    address_parts.append(element['tags'][addr_key])
            address = ', '.join(address_parts) if address_parts else name
            image = images.get(category, "icons/supermarket.png")
            osm_points.append({
                "Zone": None,  # sera corrigé plus tard
                "Nom": name,
                "Catégorie": category,
                "Statut": statut,
                "Adresse": address,
                "Latitude": lat,
                "Longitude": lon,
                "Image": image,
                "Source": "OSM"
            })
    # --- Collecte ATP/AllThePlaces ---
    atp_points = []
    atp_file = "points_vente_casablanca_atp.csv"
    if not os.path.exists(atp_file):
        print(f"   [INFO] Génération automatique du fichier ATP: {atp_file}")
        atp_data = [
            {
                "Nom": "ATP Market 1",
                "Catégorie": "Supermarché",
                "Statut": "Formel",
                "Adresse": "Rue 1, Casablanca",
                "Latitude": 33.573,
                "Longitude": -7.620,
                "Image": "icons/supermarket.png"
            },
            {
                "Nom": "ATP Epicerie 2",
                "Catégorie": "Épicerie",
                "Statut": "Informel",
                "Adresse": "Rue 2, Casablanca",
                "Latitude": 33.580,
                "Longitude": -7.630,
                "Image": "icons/greengrocer.png"
            },
            {
                "Nom": "ATP Café 3",
                "Catégorie": "Café",
                "Statut": "Formel",
                "Adresse": "Rue 3, Casablanca",
                "Latitude": 33.590,
                "Longitude": -7.640,
                "Image": "icons/cafe.png"
            }
        ]
        df_atp = pd.DataFrame(atp_data)
        df_atp.to_csv(atp_file, index=False, encoding='utf-8-sig')
        print(f"   [SUCCESS] Fichier ATP créé avec {len(df_atp)} points")
    else:
        print(f"[INFO] Chargement des donnees ATP depuis {atp_file}")
        df_atp = pd.read_csv(atp_file)
    for _, row in df_atp.iterrows():
        atp_points.append({
            "Zone": None,  # sera corrigé plus tard
            "Nom": row.get("Nom", "ATP sans nom"),
            "Catégorie": row.get("Catégorie", "Non défini"),
            "Statut": row.get("Statut", "Non défini"),
            "Adresse": row.get("Adresse", ""),
            "Latitude": row.get("Latitude", None),
            "Longitude": row.get("Longitude", None),
            "Image": row.get("Image", ""),
            "Source": "ATP"
        })
    print(f"   [SUCCESS] {len(df_atp)} points ATP charges")
    # --- Fusion des points ---
    all_points = osm_points + atp_points
    if not all_points:
        print("[ERROR] Aucun point de vente valide trouve")
        return
    df = pd.DataFrame(all_points)
    # --- Correction des zones ---
    zone_mapping = {
        (33.593, 33.600, -7.630, -7.610): "Centre-Ville",
        (33.575, 33.590, -7.650, -7.630): "Maarif",
        (33.570, 33.580, -7.680, -7.650): "Ain Diab",
        (33.590, 33.610, -7.670, -7.640): "Anfa",
        (33.560, 33.580, -7.650, -7.620): "Hay Hassani",
        (33.610, 33.630, -7.550, -7.520): "Sidi Bernoussi",
        (33.600, 33.620, -7.540, -7.500): "Ain Sebaa",
        (33.680, 33.700, -7.390, -7.350): "Mohammedia",
        (33.450, 33.480, -7.650, -7.600): "Bouskoura",
        (33.360, 33.400, -7.600, -7.550): "Nouaceur",
        (33.450, 33.480, -7.550, -7.500): "Mediouna",
        (33.540, 33.570, -7.490, -7.460): "Tit Mellil",
        (33.630, 33.650, -7.460, -7.430): "Ain Harrouda",
    }
    def get_zone_from_coords(lat, lon):
        if pd.isna(lat) or pd.isna(lon):
            return "Casablanca"
        for (lat_min, lat_max, lon_min, lon_max), zone_name in zone_mapping.items():
            if lat_min <= lat <= lat_max and lon_min <= lon <= lon_max:
                return zone_name
        return "Marrakech"
    df["Zone"] = df.apply(lambda row: get_zone_from_coords(row["Latitude"], row["Longitude"]), axis=1)
    # --- Nettoyage et stats ---
    initial_count = len(df)
    df = df.drop_duplicates(subset=["Nom", "Latitude", "Longitude"], keep='first')
    final_count = len(df)
    print(f"[INFO] {initial_count - final_count} doublons supprimes")
    print(f"\n[INFO] Repartition par categorie:")
    category_stats = df['Catégorie'].value_counts()
    for category, count in category_stats.items():
        print(f"   {category}: {count}")
    print(f"\n[INFO] Repartition par statut:")
    status_stats = df['Statut'].value_counts()
    for status, count in status_stats.items():
        print(f"   {status}: {count}")
    # --- Sauvegarde ---
    output_file = "points_vente_marrakech_complet.csv"
    csv_ok = False
    try:
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"\n[SUCCESS] {final_count} points de vente sauvegardes dans {output_file}")
        csv_ok = True
    except PermissionError:
        output_file = f"points_vente_casablanca_complet_{int(time.time())}.csv"
        try:
            df.to_csv(output_file, index=False, encoding='utf-8-sig')
            print(f"\n[SUCCESS] {final_count} points de vente sauvegardes dans {output_file}")
            csv_ok = True
        except Exception as e:
            print(f"[ERROR] Impossible de sauvegarder le CSV: {e}")

    # --- Génération du tableau HTML ---
    html_file = output_file.replace('.csv', '.html')
    html_ok = False
    try:
        df_html = df.to_html(index=False, escape=False)
        with open(html_file, 'w', encoding='utf-8-sig') as f:
            f.write(df_html)
        print(f"[SUCCESS] Tableau HTML généré dans {html_file}")
        html_ok = True
    except Exception as e:
        print(f"[ERROR] Impossible de générer le HTML: {e}")

    # --- Vérification automatique des fichiers ---
    if not csv_ok or not os.path.exists(output_file):
        print(f"[ERROR] Le fichier CSV n'a pas été généré: {output_file}")
    if not html_ok or not os.path.exists(html_file):
        print(f"[ERROR] Le fichier HTML n'a pas été généré: {html_file}")

if __name__ == "__main__":
    main()