"""
Gestionnaire de données avec versioning et historique
Gère la fusion, mise à jour et sauvegarde des données de scraping
"""

import pandas as pd
import os
import json
import shutil
from datetime import datetime
from pathlib import Path
from duplicate_detection import merge_with_existing, remove_duplicates

# ============================================================================
# CONFIGURATION
# ============================================================================

# Dossiers
DATA_DIR = Path("data")
LOGS_DIR = Path("logs")
BACKUP_DIR = Path("backups")
HISTORY_DIR = Path("history")

# S'assurer que les dossiers existent
for directory in [DATA_DIR, LOGS_DIR, BACKUP_DIR, HISTORY_DIR]:
    directory.mkdir(exist_ok=True)

# ============================================================================
# CLASSE PRINCIPALE
# ============================================================================

class DataManager:
    """Gestionnaire de données avec versioning"""
    
    def __init__(self, zone_name, verbose=True):
        """
        Initialise le gestionnaire pour une zone spécifique
        
        Args:
            zone_name: Nom de la zone (ex: "Casablanca", "Rabat", "Region_Tanger")
            verbose: Afficher les logs détaillés
        """
        self.zone_name = zone_name
        self.verbose = verbose
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Fichiers
        self.csv_file = DATA_DIR / f"points_vente_{zone_name.lower().replace(' ', '_')}_complet.csv"
        self.log_file = LOGS_DIR / f"{zone_name.lower().replace(' ', '_')}_{self.timestamp}.log"
        self.history_file = HISTORY_DIR / f"{zone_name.lower().replace(' ', '_')}_history.json"
        
        # Initialiser le log
        self.log_entries = []
        self._log(f"📝 DataManager initialisé pour: {zone_name}")
    
    def _log(self, message, level="INFO"):
        """Ajoute une entrée au log"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        self.log_entries.append(log_entry)
        
        if self.verbose:
            print(log_entry)
    
    def _save_logs(self):
        """Sauvegarde les logs dans un fichier"""
        try:
            with open(self.log_file, 'w', encoding='utf-8') as f:
                f.write("\n".join(self.log_entries))
            self._log(f"✅ Logs sauvegardés: {self.log_file}")
        except Exception as e:
            print(f"❌ Erreur sauvegarde logs: {e}")
    
    def _create_backup(self):
        """Crée une backup du fichier existant"""
        if not self.csv_file.exists():
            self._log("ℹ️  Pas de fichier existant à sauvegarder")
            return None
        
        try:
            backup_file = BACKUP_DIR / f"{self.csv_file.stem}_{self.timestamp}.csv"
            shutil.copy2(self.csv_file, backup_file)
            self._log(f"💾 Backup créée: {backup_file}")
            return backup_file
        except Exception as e:
            self._log(f"❌ Erreur création backup: {e}", "ERROR")
            return None
    
    def _load_existing_data(self):
        """Charge les données existantes"""
        if not self.csv_file.exists():
            self._log("ℹ️  Aucune donnée existante")
            return pd.DataFrame()
        
        try:
            df = pd.read_csv(self.csv_file, encoding='utf-8-sig')
            self._log(f"📂 Chargé {len(df)} entrées existantes")
            return df
        except Exception as e:
            self._log(f"❌ Erreur chargement: {e}", "ERROR")
            return pd.DataFrame()
    
    def _update_history(self, stats, operation="update"):
        """Met à jour l'historique JSON"""
        # Charger l'historique existant
        if self.history_file.exists():
            with open(self.history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
        else:
            history = {
                "zone": self.zone_name,
                "created_at": datetime.now().isoformat(),
                "updates": []
            }
        
        # Ajouter la nouvelle entrée
        history["updates"].append({
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "stats": stats,
            "log_file": str(self.log_file.name),
            "backup_file": str(self.backup_file.name) if hasattr(self, 'backup_file') and self.backup_file else None
        })
        
        # Sauvegarder
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
        
        self._log(f"📜 Historique mis à jour: {self.history_file}")
    
    def save_data(self, df, stats=None):
        """
        Sauvegarde les données dans le CSV
        
        Args:
            df: DataFrame à sauvegarder
            stats: Statistiques optionnelles de l'opération
        """
        try:
            # Créer backup avant de sauvegarder
            self.backup_file = self._create_backup()
            
            # Sauvegarder le nouveau CSV
            df.to_csv(self.csv_file, index=False, encoding='utf-8-sig')
            self._log(f"💾 Sauvegardé {len(df)} entrées: {self.csv_file}")
            
            # Mettre à jour l'historique
            if stats:
                self._update_history(stats, "save")
            
            # Sauvegarder les logs
            self._save_logs()
            
            return True
        except Exception as e:
            self._log(f"❌ Erreur sauvegarde: {e}", "ERROR")
            return False
    
    def add_new_data(self, new_df, duplicate_strategy='keep_first', skip_duplicate_detection=False):
        """
        Ajoute de nouvelles données en gérant intelligemment les doublons
        
        Args:
            new_df: DataFrame avec les nouvelles données
            duplicate_strategy: Stratégie de gestion des doublons
            skip_duplicate_detection: Si True, skip la détection (mode rapide)
        
        Returns:
            DataFrame fusionné, statistiques
        """
        self._log(f"🔄 Début de la fusion de {len(new_df)} nouvelles entrées")
        
        if skip_duplicate_detection:
            self._log(f"⚡ MODE RAPIDE: Détection de doublons désactivée")
        
        # Charger les données existantes
        existing_df = self._load_existing_data()
        
        if existing_df.empty:
            # Pas de données existantes
            self._log("📝 Première importation pour cette zone")
            
            if skip_duplicate_detection:
                # Mode rapide : pas de nettoyage
                clean_df = new_df
                removed = []
            else:
                # Nettoyer les doublons internes
                clean_df, removed = remove_duplicates(new_df, strategy=duplicate_strategy, verbose=self.verbose)
            
            stats = {
                'added': len(clean_df),
                'updated': 0,
                'ignored': 0,
                'duplicates_removed': len(removed),
                'total_before': len(new_df),
                'total_after': len(clean_df),
                'operation': 'initial_import'
            }
        else:
            # Fusion intelligente
            self._log(f"🔄 Fusion avec {len(existing_df)} entrées existantes")
            
            if skip_duplicate_detection:
                # Mode rapide : simple concaténation
                merged_df = pd.concat([existing_df, new_df], ignore_index=True)
                merge_stats = {
                    'added': len(new_df),
                    'updated': 0,
                    'ignored': 0
                }
                removed = []
                clean_df = merged_df
            else:
                # Mode normal : fusion intelligente
                merged_df, merge_stats = merge_with_existing(new_df, existing_df, verbose=self.verbose)
                # Nettoyer les doublons dans le résultat final
                clean_df, removed = remove_duplicates(merged_df, strategy=duplicate_strategy, verbose=self.verbose)
            
            stats = {
                'added': merge_stats['added'],
                'updated': merge_stats['updated'],
                'ignored': merge_stats['ignored'],
                'duplicates_removed': len(removed),
                'total_before': len(existing_df),
                'total_after': len(clean_df),
                'operation': 'merge'
            }
        
        # Log des statistiques
        self._log("=" * 60)
        self._log("📊 STATISTIQUES DE FUSION")
        self._log("=" * 60)
        self._log(f"   ➕ Nouveaux ajoutés: {stats['added']}")
        self._log(f"   ✏️  Mis à jour: {stats['updated']}")
        self._log(f"   ⏭️  Ignorés (doublons): {stats['ignored']}")
        self._log(f"   🗑️  Doublons internes supprimés: {stats['duplicates_removed']}")
        self._log(f"   📊 Total avant: {stats['total_before']}")
        self._log(f"   📊 Total après: {stats['total_after']}")
        self._log("=" * 60)
        
        return clean_df, stats
    
    def update_data(self, new_df, duplicate_strategy='keep_best', skip_duplicate_detection=False):
        """
        Met à jour les données existantes avec de nouvelles données
        
        Args:
            new_df: DataFrame avec les nouvelles données
            duplicate_strategy: Stratégie pour gérer les doublons
            skip_duplicate_detection: Si True, skip la détection de doublons (mode rapide)
        
        Returns:
            True si succès, False sinon
        """
        try:
            # Fusionner et nettoyer
            final_df, stats = self.add_new_data(new_df, duplicate_strategy, skip_duplicate_detection)
            
            # Sauvegarder
            success = self.save_data(final_df, stats)
            
            if success:
                self._log("✅ Mise à jour terminée avec succès")
            else:
                self._log("❌ Échec de la mise à jour", "ERROR")
            
            return success
        except Exception as e:
            self._log(f"❌ Erreur durant la mise à jour: {e}", "ERROR")
            return False
    
    def get_history(self):
        """Récupère l'historique des mises à jour"""
        if not self.history_file.exists():
            return None
        
        with open(self.history_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_stats_summary(self):
        """Récupère un résumé des statistiques"""
        history = self.get_history()
        if not history:
            return None
        
        total_updates = len(history['updates'])
        total_added = sum(u['stats'].get('added', 0) for u in history['updates'])
        total_updated = sum(u['stats'].get('updated', 0) for u in history['updates'])
        
        current_count = 0
        if self.csv_file.exists():
            df = pd.read_csv(self.csv_file)
            current_count = len(df)
        
        return {
            'zone': self.zone_name,
            'total_updates': total_updates,
            'total_added': total_added,
            'total_updated': total_updated,
            'current_count': current_count,
            'last_update': history['updates'][-1]['timestamp'] if history['updates'] else None
        }

# ============================================================================
# FONCTIONS UTILITAIRES
# ============================================================================

def get_all_zones_history():
    """Récupère l'historique de toutes les zones"""
    histories = []
    
    for history_file in HISTORY_DIR.glob("*_history.json"):
        with open(history_file, 'r', encoding='utf-8') as f:
            history = json.load(f)
            histories.append(history)
    
    return histories

def get_global_stats():
    """Statistiques globales de toutes les zones"""
    all_histories = get_all_zones_history()
    
    total_zones = len(all_histories)
    total_points = 0
    total_updates = 0
    
    for history in all_histories:
        zone_name = history['zone']
        csv_file = DATA_DIR / f"points_vente_{zone_name.lower().replace(' ', '_')}_complet.csv"
        
        if csv_file.exists():
            df = pd.read_csv(csv_file)
            total_points += len(df)
        
        total_updates += len(history.get('updates', []))
    
    return {
        'total_zones': total_zones,
        'total_points': total_points,
        'total_updates': total_updates
    }

def cleanup_old_backups(days=30):
    """Supprime les backups plus anciens que X jours"""
    import time
    
    cutoff_time = time.time() - (days * 86400)
    deleted = 0
    
    for backup_file in BACKUP_DIR.glob("*.csv"):
        if backup_file.stat().st_mtime < cutoff_time:
            backup_file.unlink()
            deleted += 1
    
    print(f"🗑️  {deleted} backups supprimés (> {days} jours)")
    return deleted

# ============================================================================
# TESTS
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("TEST DU GESTIONNAIRE DE DONNÉES")
    print("=" * 80)
    
    # Test de données
    test_data = pd.DataFrame([
        {"Zone": "Test", "Nom": "Point Test 1", "Latitude": 33.5, "Longitude": -7.6, 
         "Catégorie": "Supermarché", "Statut": "Formel", "Source": "OSM"},
        {"Zone": "Test", "Nom": "Point Test 2", "Latitude": 33.6, "Longitude": -7.7, 
         "Catégorie": "Épicerie", "Statut": "Informel", "Source": "ATP"},
    ])
    
    # Créer un gestionnaire
    manager = DataManager("Test_Zone")
    
    # Ajouter des données
    manager.update_data(test_data)
    
    # Afficher les stats
    stats = manager.get_stats_summary()
    if stats:
        print("\n📊 Statistiques:")
        for key, value in stats.items():
            print(f"   {key}: {value}")
    
    print("\n✅ Test terminé!")
