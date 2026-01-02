"""
Configuration des zones géographiques du Maroc
Inclut les 12 régions administratives et les principales villes
Bbox format: (lat_min, lon_min, lat_max, lon_max)
"""

# ============================================================================
# RÉGIONS ADMINISTRATIVES DU MAROC (12 régions)
# ============================================================================

REGIONS = {
    "Tanger-Tétouan-Al Hoceïma": {
        "bbox": "34.5,-6.5,36.0,-4.0",
        "description": "Région du nord incluant Tanger, Tétouan, Al Hoceïma",
        "population_estimate": 3556729
    },
    "L'Oriental": {
        "bbox": "33.5,-3.5,35.0,-1.0",
        "description": "Région de l'est incluant Oujda, Nador, Berkane",
        "population_estimate": 2314346
    },
    "Fès-Meknès": {
        "bbox": "33.0,-6.0,34.5,-4.0",
        "description": "Région centrale incluant Fès, Meknès, Ifrane",
        "population_estimate": 4236892
    },
    "Rabat-Salé-Kénitra": {
        "bbox": "33.5,-7.5,35.0,-6.0",
        "description": "Région de la capitale incluant Rabat, Salé, Kénitra",
        "population_estimate": 4580866
    },
    "Béni Mellal-Khénifra": {
        "bbox": "31.5,-7.5,33.5,-5.0",
        "description": "Région centrale incluant Béni Mellal, Khénifra",
        "population_estimate": 2520776
    },
    "Casablanca-Settat": {
        "bbox": "32.5,-8.5,34.0,-6.5",
        "description": "Région économique incluant Casablanca, Settat, El Jadida",
        "population_estimate": 6861739
    },
    "Marrakech-Safi": {
        "bbox": "31.0,-10.0,32.5,-7.5",
        "description": "Région touristique incluant Marrakech, Safi, Essaouira",
        "population_estimate": 4520569
    },
    "Drâa-Tafilalet": {
        "bbox": "30.0,-7.0,32.0,-4.0",
        "description": "Région du sud-est incluant Errachidia, Ouarzazate, Zagora",
        "population_estimate": 1635008
    },
    "Souss-Massa": {
        "bbox": "29.0,-10.5,31.0,-8.0",
        "description": "Région du sud incluant Agadir, Tiznit, Taroudant",
        "population_estimate": 2676847
    },
    "Guelmim-Oued Noun": {
        "bbox": "27.5,-11.5,29.5,-9.0",
        "description": "Région du sud incluant Guelmim, Tan-Tan",
        "population_estimate": 433757
    },
    "Laâyoune-Sakia El Hamra": {
        "bbox": "26.0,-14.5,28.0,-11.0",
        "description": "Région du sud incluant Laâyoune, Boujdour",
        "population_estimate": 367758
    },
    "Dakhla-Oued Ed-Dahab": {
        "bbox": "22.5,-17.0,24.5,-14.0",
        "description": "Région la plus au sud incluant Dakhla",
        "population_estimate": 142955
    }
}

# ============================================================================
# GRANDES VILLES DU MAROC (par ordre de population)
# ============================================================================

CITIES = {
    # Top 10 villes par population
    "Casablanca": {
        "bbox": "33.45,-7.75,33.65,-7.45",
        "region": "Casablanca-Settat",
        "population": 3359818,
        "zones": [
            {"name": "Centre-Ville", "bbox": "33.593,-7.630,33.600,-7.610"},
            {"name": "Maarif", "bbox": "33.575,-7.650,33.590,-7.630"},
            {"name": "Ain Diab", "bbox": "33.570,-7.680,33.580,-7.650"},
            {"name": "Anfa", "bbox": "33.590,-7.670,33.610,-7.640"},
            {"name": "Hay Hassani", "bbox": "33.560,-7.650,33.580,-7.620"},
            {"name": "Sidi Bernoussi", "bbox": "33.610,-7.550,33.630,-7.520"},
            {"name": "Ain Sebaa", "bbox": "33.600,-7.540,33.620,-7.500"},
            {"name": "Bouskoura", "bbox": "33.450,-7.650,33.480,-7.600"},
        ]
    },
    "Rabat": {
        "bbox": "33.95,-6.95,34.05,-6.75",
        "region": "Rabat-Salé-Kénitra",
        "population": 577827,
        "zones": [
            {"name": "Agdal", "bbox": "33.970,-6.870,34.000,-6.840"},
            {"name": "Hassan", "bbox": "34.010,-6.840,34.030,-6.820"},
            {"name": "Souissi", "bbox": "33.970,-6.900,34.000,-6.870"},
            {"name": "Océan", "bbox": "34.010,-6.870,34.040,-6.840"},
        ]
    },
    "Fès": {
        "bbox": "34.00,-5.10,34.10,-4.95",
        "region": "Fès-Meknès",
        "population": 1150131,
        "zones": [
            {"name": "Médina", "bbox": "34.055,-5.005,34.070,-4.975"},
            {"name": "Ville Nouvelle", "bbox": "34.030,-5.030,34.055,-5.000"},
            {"name": "Zouagha", "bbox": "34.020,-5.060,34.040,-5.030"},
        ]
    },
    "Marrakech": {
        "bbox": "31.53,-8.10,31.70,-7.90",
        "region": "Marrakech-Safi",
        "population": 928850,
        "zones": [
            {"name": "Médina", "bbox": "31.620,-8.020,31.640,-7.980"},
            {"name": "Guéliz", "bbox": "31.630,-8.030,31.650,-8.000"},
            {"name": "Hivernage", "bbox": "31.610,-8.030,31.630,-8.000"},
            {"name": "Agdal", "bbox": "31.590,-8.020,31.620,-7.980"},
        ]
    },
    "Tanger": {
        "bbox": "35.70,-5.90,35.85,-5.70",
        "region": "Tanger-Tétouan-Al Hoceïma",
        "population": 947952,
        "zones": [
            {"name": "Centre", "bbox": "35.765,-5.825,35.785,-5.795"},
            {"name": "Malabata", "bbox": "35.745,-5.795,35.765,-5.765"},
            {"name": "Boubana", "bbox": "35.785,-5.850,35.810,-5.820"},
        ]
    },
    "Salé": {
        "bbox": "34.00,-6.85,34.10,-6.75",
        "region": "Rabat-Salé-Kénitra",
        "population": 890403,
        "zones": [
            {"name": "Médina", "bbox": "34.035,-6.820,34.055,-6.795"},
            {"name": "Tabriquet", "bbox": "34.055,-6.820,34.075,-6.790"},
        ]
    },
    "Meknès": {
        "bbox": "33.85,-5.60,33.95,-5.50",
        "region": "Fès-Meknès",
        "population": 632079,
        "zones": [
            {"name": "Médina", "bbox": "33.890,-5.570,33.910,-5.540"},
            {"name": "Hamriya", "bbox": "33.870,-5.590,33.895,-5.560"},
        ]
    },
    "Oujda": {
        "bbox": "34.62,-1.95,34.72,-1.85",
        "region": "L'Oriental",
        "population": 494252,
        "zones": [
            {"name": "Centre", "bbox": "34.675,-1.920,34.695,-1.895"},
            {"name": "Sidi Maafa", "bbox": "34.655,-1.945,34.675,-1.920"},
        ]
    },
    "Kénitra": {
        "bbox": "34.20,-6.65,34.30,-6.55",
        "region": "Rabat-Salé-Kénitra",
        "population": 431282,
        "zones": [
            {"name": "Centre", "bbox": "34.250,-6.600,34.270,-6.575"},
            {"name": "Saknia", "bbox": "34.230,-6.625,34.250,-6.600"},
        ]
    },
    "Agadir": {
        "bbox": "30.35,-9.65,30.50,-9.50",
        "region": "Souss-Massa",
        "population": 421844,
        "zones": [
            {"name": "Centre", "bbox": "30.415,-9.610,30.435,-9.580"},
            {"name": "Founty", "bbox": "30.395,-9.640,30.420,-9.610"},
            {"name": "Talborjt", "bbox": "30.435,-9.610,30.460,-9.580"},
        ]
    },
    "Tétouan": {
        "bbox": "35.53,-5.42,35.63,-5.32",
        "region": "Tanger-Tétouan-Al Hoceïma",
        "population": 380787,
        "zones": [
            {"name": "Médina", "bbox": "35.570,-5.375,35.585,-5.355"},
            {"name": "Ensanche", "bbox": "35.575,-5.385,35.595,-5.360"},
        ]
    },
    "Al Hoceïma": {
        "bbox": "35.20,-3.95,35.30,-3.85",
        "region": "Tanger-Tétouan-Al Hoceïma",
        "population": 56716,
        "zones": []
    },
    "Nador": {
        "bbox": "35.10,-2.95,35.20,-2.85",
        "region": "L'Oriental",
        "population": 161726,
        "zones": []
    },
    "Béni Mellal": {
        "bbox": "32.30,-6.45,32.40,-6.30",
        "region": "Béni Mellal-Khénifra",
        "population": 192676,
        "zones": []
    },
    "Settat": {
        "bbox": "32.95,-7.70,33.05,-7.60",
        "region": "Casablanca-Settat",
        "population": 142250,
        "zones": []
    },
    "El Jadida": {
        "bbox": "33.20,-8.55,33.30,-8.45",
        "region": "Casablanca-Settat",
        "population": 194934,
        "zones": []
    },
    "Safi": {
        "bbox": "32.25,-9.30,32.35,-9.20",
        "region": "Marrakech-Safi",
        "population": 308508,
        "zones": []
    },
    "Essaouira": {
        "bbox": "31.45,-9.85,31.55,-9.75",
        "region": "Marrakech-Safi",
        "population": 77966,
        "zones": []
    },
    "Khénifra": {
        "bbox": "32.90,-5.75,33.00,-5.60",
        "region": "Béni Mellal-Khénifra",
        "population": 117510,
        "zones": []
    },
    "Errachidia": {
        "bbox": "31.88,-4.50,31.98,-4.40",
        "region": "Drâa-Tafilalet",
        "population": 92374,
        "zones": []
    },
    "Ouarzazate": {
        "bbox": "30.88,-6.98,30.98,-6.88",
        "region": "Drâa-Tafilalet",
        "population": 71067,
        "zones": []
    },
    "Taroudant": {
        "bbox": "30.43,-8.93,30.53,-8.83",
        "region": "Souss-Massa",
        "population": 80149,
        "zones": []
    },
    "Tiznit": {
        "bbox": "29.65,-9.80,29.75,-9.70",
        "region": "Souss-Massa",
        "population": 74699,
        "zones": []
    },
    "Guelmim": {
        "bbox": "28.95,-10.15,29.05,-10.05",
        "region": "Guelmim-Oued Noun",
        "population": 118318,
        "zones": []
    },
    "Laâyoune": {
        "bbox": "27.10,-13.25,27.20,-13.15",
        "region": "Laâyoune-Sakia El Hamra",
        "population": 217732,
        "zones": []
    },
    "Dakhla": {
        "bbox": "23.65,-15.98,23.75,-15.88",
        "region": "Dakhla-Oued Ed-Dahab",
        "population": 106277,
        "zones": []
    },
}

# ============================================================================
# FONCTIONS UTILITAIRES
# ============================================================================

def get_all_zones():
    """Retourne toutes les zones (régions + villes)"""
    zones = {}
    
    # Ajouter toutes les régions
    for region_name, region_data in REGIONS.items():
        zones[f"Région: {region_name}"] = {
            "type": "region",
            "name": region_name,
            "bbox": region_data["bbox"],
            "description": region_data["description"],
            "output_file": f"points_vente_{region_name.lower().replace(' ', '_').replace('-', '_')}_complet.csv"
        }
    
    # Ajouter toutes les villes
    for city_name, city_data in CITIES.items():
        zones[f"Ville: {city_name}"] = {
            "type": "city",
            "name": city_name,
            "bbox": city_data["bbox"],
            "region": city_data["region"],
            "population": city_data.get("population", 0),
            "output_file": f"points_vente_{city_name.lower().replace(' ', '_')}_complet.csv"
        }
        
        # Ajouter les sous-zones de la ville si disponibles
        if city_data.get("zones"):
            for subzone in city_data["zones"]:
                zones[f"  └─ {city_name} - {subzone['name']}"] = {
                    "type": "subzone",
                    "city": city_name,
                    "name": subzone["name"],
                    "bbox": subzone["bbox"],
                    "output_file": f"points_vente_{city_name.lower()}_{subzone['name'].lower().replace(' ', '_')}_complet.csv"
                }
    
    return zones

def get_bbox_from_string(bbox_string):
    """Convertit une chaîne bbox en tuple (lat_min, lon_min, lat_max, lon_max)"""
    parts = bbox_string.split(',')
    return tuple(map(float, parts))

def format_bbox_for_overpass(lat_min, lon_min, lat_max, lon_max):
    """Formate les coordonnées pour l'API Overpass"""
    return f"{lat_min},{lon_min},{lat_max},{lon_max}"

def get_zones_by_type(zone_type):
    """
    Récupère les zones par type
    zone_type: 'region', 'city', 'subzone', ou 'all'
    """
    all_zones = get_all_zones()
    if zone_type == 'all':
        return all_zones
    return {k: v for k, v in all_zones.items() if v['type'] == zone_type}

def get_zone_by_name(zone_name):
    """Récupère une zone spécifique par son nom"""
    all_zones = get_all_zones()
    for key, zone_data in all_zones.items():
        if zone_data['name'] == zone_name:
            return zone_data
    return None

def get_morocco_full_bbox():
    """Retourne le bbox complet du Maroc"""
    return "27.5,-17.0,36.0,-1.0"

# ============================================================================
# CONFIGURATION DE SCRAPING
# ============================================================================

SCRAPING_CONFIG = {
    "timeout": 120,  # secondes
    "retry_attempts": 3,
    "retry_delay": 5,  # secondes
    "rate_limit_delay": 2,  # délai entre requêtes pour éviter le throttling
    "batch_size": 5,  # nombre de zones à scraper en parallèle
}

# ============================================================================
# EXPORT
# ============================================================================

if __name__ == "__main__":
    # Test des fonctions
    print("=" * 80)
    print("CONFIGURATION DES ZONES DU MAROC")
    print("=" * 80)
    
    print(f"\n📍 Total de régions: {len(REGIONS)}")
    print(f"📍 Total de villes: {len(CITIES)}")
    
    all_zones = get_all_zones()
    print(f"📍 Total de zones disponibles: {len(all_zones)}")
    
    print("\n🗺️ Aperçu des zones:")
    for zone_name, zone_data in list(all_zones.items())[:10]:
        print(f"  - {zone_name}: {zone_data['bbox']}")
    
    print("\n✅ Configuration chargée avec succès!")
