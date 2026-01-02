"""
Module de détection de doublons - Industry Grade
Utilise plusieurs techniques de matching:
1. Fuzzy matching sur les noms (Levenshtein distance)
2. Distance géographique (Haversine)
3. Scoring combiné pour décision intelligente
"""

import pandas as pd
import numpy as np
from math import radians, cos, sin, asin, sqrt
from difflib import SequenceMatcher

# ============================================================================
# CONFIGURATION
# ============================================================================

# Seuils de détection (ajustables selon vos besoins)
CONFIG = {
    "name_similarity_threshold": 0.85,  # 85% de similarité des noms
    "distance_threshold_meters": 50,     # 50 mètres de rayon
    "combined_score_threshold": 0.75,    # Score combiné minimum pour doublon
    "weights": {
        "name": 0.6,      # Poids du nom dans le score final
        "distance": 0.4,  # Poids de la distance dans le score final
    }
}

# ============================================================================
# FONCTIONS DE CALCUL DE DISTANCE
# ============================================================================

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calcule la distance entre deux points GPS en mètres
    Utilise la formule de Haversine (précision industry-grade)
    """
    # Conversion en radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    # Formule de Haversine
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    
    # Rayon de la Terre en mètres
    r = 6371000
    
    return c * r

def is_within_radius(lat1, lon1, lat2, lon2, radius_meters):
    """Vérifie si deux points sont dans un rayon donné"""
    distance = haversine_distance(lat1, lon1, lat2, lon2)
    return distance <= radius_meters, distance

# ============================================================================
# FONCTIONS DE SIMILARITÉ DE TEXTE
# ============================================================================

def normalize_text(text):
    """Normalise le texte pour comparaison"""
    if pd.isna(text):
        return ""
    text = str(text).lower().strip()
    # Suppression des caractères spéciaux communs
    text = text.replace("é", "e").replace("è", "e").replace("ê", "e")
    text = text.replace("à", "a").replace("â", "a")
    text = text.replace("ô", "o").replace("ö", "o")
    text = text.replace("ù", "u").replace("û", "u")
    text = text.replace("ç", "c")
    text = text.replace("'", " ").replace("-", " ")
    # Suppression espaces multiples
    text = " ".join(text.split())
    return text

def levenshtein_distance(s1, s2):
    """
    Calcule la distance de Levenshtein entre deux chaînes
    (nombre minimum d'opérations pour transformer s1 en s2)
    """
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    
    if len(s2) == 0:
        return len(s1)
    
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            # Coût d'insertion, suppression, substitution
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]

def text_similarity(text1, text2):
    """
    Calcule la similarité entre deux textes (0 à 1)
    Combine plusieurs méthodes pour plus de robustesse
    """
    # Normalisation
    text1_norm = normalize_text(text1)
    text2_norm = normalize_text(text2)
    
    if not text1_norm or not text2_norm:
        return 0.0
    
    # Méthode 1: SequenceMatcher (rapide)
    similarity_quick = SequenceMatcher(None, text1_norm, text2_norm).ratio()
    
    # Méthode 2: Levenshtein normalisé (plus précis)
    max_len = max(len(text1_norm), len(text2_norm))
    lev_dist = levenshtein_distance(text1_norm, text2_norm)
    similarity_lev = 1 - (lev_dist / max_len)
    
    # Méthode 3: Token-based (pour noms avec ordre différent)
    tokens1 = set(text1_norm.split())
    tokens2 = set(text2_norm.split())
    if tokens1 and tokens2:
        intersection = tokens1.intersection(tokens2)
        union = tokens1.union(tokens2)
        similarity_token = len(intersection) / len(union)
    else:
        similarity_token = 0.0
    
    # Moyenne pondérée des trois méthodes
    final_similarity = (
        0.4 * similarity_quick +
        0.4 * similarity_lev +
        0.2 * similarity_token
    )
    
    return final_similarity

# ============================================================================
# DÉTECTION DE DOUBLONS
# ============================================================================

def find_duplicates_fast(df, config=None, verbose=True):
    """
    Détection OPTIMISÉE avec grille spatiale - 7x plus rapide !
    
    Principe :
    1. Diviser la zone en carrés de ~1km (grille)
    2. Comparer seulement les points dans le MÊME carré ou carrés adjacents
    3. Réduction de O(n²) à O(k × m²) où k=nb carrés, m=points/carré
    
    Exemple :
    - Sans grille : 2105 points → 2,2M comparaisons (13 min)
    - Avec grille : 2105 points → 300K comparaisons (1-2 min)
    
    Args:
        df: DataFrame avec colonnes Latitude, Longitude, Nom
        config: Configuration des seuils (optionnel)
        verbose: Afficher la progression
    
    Returns:
        Liste de tuples (index1, index2, score) des doublons détectés
    """
    if config is None:
        config = CONFIG
    
    if len(df) < 2:
        return []
    
    df_work = df.reset_index(drop=True)
    
    # Étape 1 : Créer la grille spatiale
    # 0.01 degré ≈ 1.1 km au Maroc (latitude ~33°)
    grid_size = 0.01
    
    if verbose:
        print(f"\n🗺️  Création de la grille spatiale (taille: {grid_size:.4f}° ≈ 1km)...")
    
    df_work['grid_x'] = (df_work['Longitude'] / grid_size).astype(int)
    df_work['grid_y'] = (df_work['Latitude'] / grid_size).astype(int)
    
    # Étape 2 : Grouper par cellule
    grouped = df_work.groupby(['grid_x', 'grid_y'])
    n_cells = len(grouped)
    
    if verbose:
        print(f"📊 {len(df_work)} points répartis en {n_cells} cellules")
        avg_per_cell = len(df_work) / n_cells
        print(f"📌 Moyenne: {avg_per_cell:.1f} points/cellule")
    
    # Étape 3 : Comparer dans chaque cellule + cellules adjacentes
    duplicates = []
    total_comparisons = 0
    
    if verbose:
        print(f"\n🔍 Recherche de doublons dans les cellules...")
    
    for cell_idx, ((gx, gy), cell_group) in enumerate(grouped):
        # Points de la cellule courante
        cell_points = cell_group.index.tolist()
        
        # Collecter les points des cellules adjacentes (rayon de 1 cellule)
        adjacent_points = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                neighbor_key = (gx + dx, gy + dy)
                if neighbor_key in grouped.groups:
                    adjacent_points.extend(grouped.groups[neighbor_key].tolist())
        
        # Comparer tous les points de la cellule avec les points adjacents
        for i, idx1 in enumerate(cell_points):
            row1 = df_work.loc[idx1]
            
            for idx2 in adjacent_points:
                if idx2 <= idx1:  # Éviter doublons et auto-comparaisons
                    continue
                
                row2 = df_work.loc[idx2]
                total_comparisons += 1
                
                # Calculer le score
                score_data = calculate_duplicate_score(row1, row2, config)
                score = score_data['combined']  # FIXÉ: 'combined' au lieu de 'combined_score'
                
                if score >= config['combined_score_threshold']:
                    duplicates.append((idx1, idx2, score))
        
        # Afficher progression tous les 10%
        if verbose and (cell_idx + 1) % max(1, n_cells // 10) == 0:
            progress = (cell_idx + 1) / n_cells * 100
            print(f"   Progression: {cell_idx + 1}/{n_cells} cellules ({progress:.1f}%)")
    
    if verbose:
        print(f"✅ {len(duplicates)} doublons détectés")
        print(f"📊 Comparaisons effectuées: {total_comparisons:,}")
        
        # Estimation sans grille
        n = len(df_work)
        estimated_without_grid = n * (n - 1) // 2
        reduction = (1 - total_comparisons / estimated_without_grid) * 100 if estimated_without_grid > 0 else 0
        print(f"🚀 Réduction: {reduction:.1f}% (vs {estimated_without_grid:,} sans grille)")
    
    return duplicates

def calculate_duplicate_score(row1, row2, config=CONFIG):
    """
    Calcule un score de probabilité que deux entrées soient des doublons
    Retourne un score entre 0 (différent) et 1 (identique)
    """
    scores = {}
    
    # 1. Similarité du nom
    name_sim = text_similarity(row1.get('Nom', ''), row2.get('Nom', ''))
    scores['name'] = name_sim
    
    # 2. Distance géographique
    try:
        lat1, lon1 = float(row1['Latitude']), float(row1['Longitude'])
        lat2, lon2 = float(row2['Latitude']), float(row2['Longitude'])
        
        distance = haversine_distance(lat1, lon1, lat2, lon2)
        
        # Score inversé: plus c'est proche, plus le score est élevé
        # Si distance = 0m → score = 1
        # Si distance = threshold → score = 0
        if distance <= config['distance_threshold_meters']:
            distance_score = 1 - (distance / config['distance_threshold_meters'])
        else:
            distance_score = 0
        
        scores['distance'] = distance_score
        scores['distance_meters'] = distance
    except (ValueError, KeyError):
        scores['distance'] = 0
        scores['distance_meters'] = float('inf')
    
    # 3. Bonus: même catégorie
    if row1.get('Catégorie') == row2.get('Catégorie'):
        scores['category_match'] = 1.0
    else:
        scores['category_match'] = 0.0
    
    # 4. Bonus: même adresse
    if row1.get('Adresse') and row2.get('Adresse'):
        addr_sim = text_similarity(row1.get('Adresse', ''), row2.get('Adresse', ''))
        scores['address'] = addr_sim
    else:
        scores['address'] = 0.0
    
    # Calcul du score combiné
    combined_score = (
        config['weights']['name'] * scores['name'] +
        config['weights']['distance'] * scores['distance'] +
        0.05 * scores['category_match'] +
        0.05 * scores['address']
    )
    
    scores['combined'] = min(1.0, combined_score)
    
    return scores

def find_duplicates(df, config=None, verbose=False, use_spatial_optimization=True):
    """
    Trouve tous les doublons dans un DataFrame
    
    NOUVEAU : Sélection automatique de l'algorithme optimal
    - < 500 points : Méthode standard O(n²) (rapide de toute façon)
    - > 500 points : Grille spatiale optimisée O(k×m²) (7x plus rapide)
    
    Args:
        df: DataFrame avec colonnes Latitude, Longitude, Nom
        config: Configuration des seuils (optionnel)
        verbose: Afficher la progression
        use_spatial_optimization: True pour activer la grille (recommandé)
    
    Returns:
        Liste de dictionnaires avec infos sur les doublons
    """
    if config is None:
        config = CONFIG
    
    total = len(df)
    
    if verbose:
        print(f"\n🔍 Recherche de doublons dans {total} entrées...")
    
    # Choix automatique de l'algorithme
    if use_spatial_optimization and total > 500:
        if verbose:
            print(f"⚡ Utilisation de l'algorithme optimisé (grille spatiale)")
            print(f"   Estimation: {total * (total-1) // 2:,} comparaisons → ~{total * 150:,} comparaisons")
        
        # Utiliser la méthode rapide
        duplicates_raw = find_duplicates_fast(df, config, verbose)
        
        # Convertir au format attendu
        duplicates = []
        for idx1, idx2, score in duplicates_raw:
            row1 = df.iloc[idx1]
            row2 = df.iloc[idx2]
            
            # Recalculer les scores détaillés pour l'affichage
            scores = calculate_duplicate_score(row1, row2, config)
            scores['combined_score'] = score
            
            duplicates.append({
                'index1': idx1,
                'index2': idx2,
                'name1': row1['Nom'],
                'name2': row2['Nom'],
                'scores': scores
            })
        
        return duplicates
    
    else:
        if verbose:
            if total <= 500:
                print(f"🔹 Dataset petit ({total} points) → méthode standard")
            else:
                print(f"🔹 Optimisation désactivée → méthode standard")
    
    # Méthode standard (pour petits datasets ou si optimisation désactivée)
    duplicates = []
    
    # Comparaison par paires
    for i in range(total):
        if verbose and i % 100 == 0:
            print(f"   Progression: {i}/{total} ({i/total*100:.1f}%)")
        
        for j in range(i + 1, total):
            row1 = df.iloc[i]
            row2 = df.iloc[j]
            
            scores = calculate_duplicate_score(row1, row2, config)
            
            # Décision: est-ce un doublon ?
            if scores['combined'] >= config['combined_score_threshold']:
                duplicates.append({
                    'index1': i,
                    'index2': j,
                    'name1': row1['Nom'],
                    'name2': row2['Nom'],
                    'scores': scores
                })
    
    if verbose:
        print(f"✅ {len(duplicates)} doublons potentiels détectés")
    
    return duplicates

def remove_duplicates(df, config=CONFIG, strategy='keep_first', verbose=False):
    """
    Supprime les doublons d'un DataFrame
    
    Stratégies:
    - 'keep_first': Garde la première occurrence
    - 'keep_best': Garde celle avec le plus de données
    - 'keep_osm': Priorité aux données OSM
    - 'keep_atp': Priorité aux données ATP
    
    Retourne:
    - DataFrame nettoyé
    - Liste des doublons supprimés (pour logging)
    """
    if df.empty:
        return df, []
    
    # Trouver les doublons
    duplicates = find_duplicates(df, config, verbose)
    
    if not duplicates:
        if verbose:
            print("✅ Aucun doublon détecté")
        return df, []
    
    # Indices à supprimer
    indices_to_remove = set()
    removed_records = []
    
    for dup in duplicates:
        idx1, idx2 = dup['index1'], dup['index2']
        row1 = df.iloc[idx1]
        row2 = df.iloc[idx2]
        
        # Décision selon la stratégie
        if strategy == 'keep_first':
            to_remove = idx2
            to_keep = idx1
        
        elif strategy == 'keep_best':
            # Garde celle avec le plus de données non-nulles
            score1 = row1.notna().sum()
            score2 = row2.notna().sum()
            if score2 > score1:
                to_remove = idx1
                to_keep = idx2
            else:
                to_remove = idx2
                to_keep = idx1
        
        elif strategy == 'keep_osm':
            if row1.get('Source') == 'OSM':
                to_remove = idx2
                to_keep = idx1
            else:
                to_remove = idx1
                to_keep = idx2
        
        elif strategy == 'keep_atp':
            if row1.get('Source') == 'ATP':
                to_remove = idx2
                to_keep = idx1
            else:
                to_remove = idx1
                to_keep = idx2
        
        else:
            to_remove = idx2
            to_keep = idx1
        
        # Ne supprimer que si pas déjà marqué pour suppression
        if to_remove not in indices_to_remove:
            indices_to_remove.add(to_remove)
            removed_records.append({
                'removed': df.iloc[to_remove].to_dict(),
                'kept': df.iloc[to_keep].to_dict(),
                'scores': dup['scores']
            })
    
    # Suppression
    df_clean = df.drop(index=list(indices_to_remove)).reset_index(drop=True)
    
    if verbose:
        print(f"🗑️  {len(indices_to_remove)} doublons supprimés")
        print(f"✅ {len(df_clean)} entrées uniques conservées")
    
    return df_clean, removed_records

def merge_with_existing(new_df, existing_df, config=CONFIG, verbose=False):
    """
    Fusionne intelligemment les nouvelles données avec les existantes
    
    Logique:
    1. Identifier les doublons entre new_df et existing_df
    2. Pour les doublons: mettre à jour si nouvelles données plus complètes
    3. Ajouter les vraies nouvelles entrées
    
    Retourne:
    - DataFrame fusionné
    - Stats de fusion (ajoutés, mis à jour, ignorés)
    """
    if existing_df.empty:
        if verbose:
            print("📝 Aucune donnée existante, ajout de toutes les nouvelles entrées")
        return new_df, {'added': len(new_df), 'updated': 0, 'ignored': 0}
    
    if new_df.empty:
        if verbose:
            print("📝 Aucune nouvelle donnée")
        return existing_df, {'added': 0, 'updated': 0, 'ignored': 0}
    
    stats = {'added': 0, 'updated': 0, 'ignored': 0}
    result_df = existing_df.copy()
    
    if verbose:
        print(f"\n🔄 Fusion de {len(new_df)} nouvelles entrées avec {len(existing_df)} existantes...")
    
    for idx, new_row in new_df.iterrows():
        # Rechercher des doublons dans les données existantes
        is_duplicate = False
        
        for exist_idx, exist_row in result_df.iterrows():
            scores = calculate_duplicate_score(new_row, exist_row, config)
            
            if scores['combined'] >= config['combined_score_threshold']:
                is_duplicate = True
                
                # Décider s'il faut mettre à jour
                new_completeness = new_row.notna().sum()
                exist_completeness = exist_row.notna().sum()
                
                if new_completeness > exist_completeness:
                    # Mise à jour
                    result_df.iloc[exist_idx] = new_row
                    stats['updated'] += 1
                    if verbose:
                        print(f"   ✏️  Mis à jour: {new_row['Nom']}")
                else:
                    stats['ignored'] += 1
                    if verbose:
                        print(f"   ⏭️  Ignoré (existe déjà): {new_row['Nom']}")
                
                break
        
        if not is_duplicate:
            # Vraie nouvelle entrée
            result_df = pd.concat([result_df, new_row.to_frame().T], ignore_index=True)
            stats['added'] += 1
            if verbose:
                print(f"   ➕ Ajouté: {new_row['Nom']}")
    
    if verbose:
        print(f"\n✅ Fusion terminée:")
        print(f"   ➕ Ajoutés: {stats['added']}")
        print(f"   ✏️  Mis à jour: {stats['updated']}")
        print(f"   ⏭️  Ignorés: {stats['ignored']}")
        print(f"   📊 Total: {len(result_df)} entrées")
    
    return result_df, stats

# ============================================================================
# TESTS
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("TEST DU MODULE DE DÉTECTION DE DOUBLONS")
    print("=" * 80)
    
    # Test données
    test_data = [
        {"Nom": "Marjane Anfa", "Latitude": 33.590, "Longitude": -7.650, "Catégorie": "Supermarché", "Source": "OSM"},
        {"Nom": "Marjane ANFA", "Latitude": 33.5905, "Longitude": -7.6502, "Catégorie": "Supermarché", "Source": "ATP"},
        {"Nom": "Carrefour Maarif", "Latitude": 33.580, "Longitude": -7.640, "Catégorie": "Supermarché", "Source": "OSM"},
        {"Nom": "Epicerie Al Baraka", "Latitude": 33.570, "Longitude": -7.620, "Catégorie": "Épicerie", "Source": "OSM"},
    ]
    
    df_test = pd.DataFrame(test_data)
    
    print("\n📊 Données de test:")
    print(df_test[['Nom', 'Latitude', 'Longitude']])
    
    # Test de détection
    df_clean, removed = remove_duplicates(df_test, verbose=True)
    
    print("\n📊 Données nettoyées:")
    print(df_clean[['Nom', 'Latitude', 'Longitude']])
    
    print("\n✅ Tests terminés!")
