import streamlit as st
import pandas as pd
import plotly.express as px
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import time

# --- Configuration de la page ---
st.set_page_config(
    page_title="DataSight - Plateforme Intelligente",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS Premium / Shadcn-like style ---
st.markdown("""
<style>
    /* Import fonts */
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&display=swap');

    /* Global Typography */
    html, body, [class*="css"] {
        font-family: 'Space Grotesk', sans-serif;
        color: #222222;
    }

    /* Main background */
    .stApp {
        background-color: #f8fafc;
    }

    /* --- LOGIN FORM FIXES --- */
    
    /* Target the container where the login form lives */
    div[data-testid="stForm"] {
        background-color: white;
        border: 1px solid #e2e8f0;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
        padding: 2.5rem;
        border-radius: 16px;
    }

    /* Force all headings and labels inside the app to be dark */
    h1, h2, h3, h4, h5, h6, .stMarkdown, p, label, .stTextInput > label, div[data-testid="stMarkdownContainer"] p {
        color: #222222 !important;
    }
    
    /* Headings with primary color accent */
    h1, h2, h3 {
        font-weight: 700 !important;
        letter-spacing: -0.02em;
    }

    /* Specifically target the "Login" title if it's rendered as a heading */
    div[data-testid="stForm"] h1, 
    div[data-testid="stForm"] h2,
    div[data-testid="stForm"] h3 {
        color: #2a7ae2 !important; 
    }

    /* Fix Input Labels */
    .stTextInput label {
        color: #475569 !important;
        font-weight: 600;
        font-size: 0.9rem;
    }

    /* Fix Input Fields */
    .stTextInput input {
        color: #222222;
        background-color: #ffffff;
        border: 2px solid #e2e8f0;
        border-radius: 8px;
        padding: 0.5rem;
    }
    .stTextInput input:focus {
        border-color: #2a7ae2;
        box-shadow: 0 0 0 3px rgba(42, 122, 226, 0.1);
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e2e8f0;
    }
    
    /* Metrics */
    .metric-container {
        background-color: white;
        padding: 24px;
        border-radius: 16px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        transition: transform 0.2s ease-in-out;
    }
    .metric-container:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        border-color: #2a7ae2;
    }
    .metric-label {
        color: #64748b !important;
        font-weight: 500;
        font-size: 0.9rem;
        margin-bottom: 4px;
    }
    .metric-value {
        color: #2a7ae2 !important;
        font-weight: 700;
        font-size: 1.8rem;
    }

    /* Warning/Error Messages */
    .stAlert {
        background-color: #fef2f2;
        border: 1px solid #fecaca;
        border-radius: 12px;
    }
    .stAlert div[data-testid="stMarkdownContainer"] {
        color: #991b1b !important;
    }

    /* Buttons */
    .stButton button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        font-weight: 600;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        transition: all 0.2s;
    }
    .stButton button:hover {
        transform: scale(1.02);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }

    /* Dataframes */
    [data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid #e2e8f0;
    }
    
    /* Styled Containers (replacing custom divs) */
    [data-testid="stVerticalBlockBorderWrapper"] > div {
        background-color: white;
        border-radius: 16px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        padding: 1rem;
    }

</style>
""", unsafe_allow_html=True)

# --- Fonction de chargement des données ---
@st.cache_data
def load_data():
    """Charge les données depuis le dossier data/ (nouveau système)"""
    import os
    from pathlib import Path
    
    try:
        data_dir = Path("data")
        
        # Si le dossier data/ n'existe pas, le créer
        if not data_dir.exists():
            data_dir.mkdir(exist_ok=True)
        
        # Chercher les fichiers CSV dans data/
        csv_files = list(data_dir.glob("points_vente_*_complet.csv"))
        
        if csv_files:
            # Charger le premier fichier trouvé (ou prioriser certaines villes)
            priority_cities = ["casablanca", "marrakech", "rabat", "fes"]
            
            selected_file = None
            for city in priority_cities:
                for file in csv_files:
                    if city in file.name.lower():
                        selected_file = file
                        break
                if selected_file:
                    break
            
            # Si aucune priorité trouvée, prendre le premier
            if not selected_file:
                selected_file = csv_files[0]
            
            df = pd.read_csv(selected_file)
            city = selected_file.stem.replace("points_vente_", "").replace("_complet", "").capitalize()
            
            # Nettoyage basique
            if 'Latitude' in df.columns:
                df = df.dropna(subset=['Latitude', 'Longitude'])
            
            # Ajouter colonne Zone si manquante
            if 'Zone' not in df.columns:
                df['Zone'] = city
            
            return df, city
        else:
            # Aucun fichier trouvé, retourner un DataFrame vide avec les colonnes nécessaires
            empty_df = pd.DataFrame(columns=['Nom', 'Catégorie', 'Latitude', 'Longitude', 'Zone', 'Statut'])
            return empty_df, "Aucune donnée"
            
    except Exception as e:
        st.error(f"Erreur de chargement: {e}")
        # Retourner un DataFrame vide avec les colonnes nécessaires
        empty_df = pd.DataFrame(columns=['Nom', 'Catégorie', 'Latitude', 'Longitude', 'Zone', 'Statut'])
        return empty_df, "Erreur"

# --- Authentification ---
def setup_auth():
    # Configuration temporaire (normalement dans un fichier config.yaml sécurisé)
    config = {
        'credentials': {
            'usernames': {
                'admin': {
                    'name': 'Admin User',
                    'password': '123', # Mot de passe simple pour la démo
                    'email': 'admin@example.com',
                }
            }
        },
        'cookie': {
            'expiry_days': 30,
            'key': 'random_signature_key',
            'name': 'datasight_cookie',
        },
        'preauthorized': {'emails': []}
    }

    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
        # preauthorized=config['preauthorized'] 
    )
    return authenticator

# --- Composants UI ---
def metric_card(title, value, delta=None, prefix=""):
    st.markdown(f"""
    <div class="metric-container">
        <div class="metric-label">{title}</div>
        <div class="metric-value">{prefix}{value}</div>
        {f'<div style="color: #10b981; font-size: 0.875rem; margin-top: 4px;">↑ {delta} cette semaine</div>' if delta else ''}
    </div>
    """, unsafe_allow_html=True)

def main():
    authenticator = setup_auth()
    
    # Login Widget
    try:
        authenticator.login()
    except Exception as e:
        st.error(e)

    if st.session_state["authentication_status"]:
        # --- APP PRINCIPALE APRES LOGIN ---
        
        # Sidebar
        with st.sidebar:
            st.image("https://placehold.co/200x60/2a7ae2/ffffff?text=DataSight", use_container_width=True)
            st.write(f"Bienvenue, *{st.session_state['name']}*")
            
            st.markdown("---")
            menu = st.radio("Navigation", ["Dashboard", "Explorateur de Données", "Carte Interactive", "🧪 Labo - Scraping", "Paramètres"], label_visibility="collapsed")
            
            st.markdown("### Filtres Globaux")
            df, city = load_data()
            
            # Filtres uniquement si des données existent
            if not df.empty and 'Zone' in df.columns:
                zones_list = ["Toutes"] + sorted(df['Zone'].dropna().unique().tolist())
                selected_zone = st.selectbox("Zone", zones_list)
                
                categories_list = sorted(df['Catégorie'].unique().tolist()) if 'Catégorie' in df.columns else []
                selected_cat = st.multiselect("Catégories", categories_list, default=[])
            else:
                st.info("🔍 Aucune donnée disponible. Lancez un scraping dans '🧪 Labo - Scraping'")
                selected_zone = "Toutes"
                selected_cat = []
            
            st.markdown("---")
            authenticator.logout('Déconnexion', 'sidebar')

        # Filtrage
        filtered_df = df.copy()
        if not df.empty:
            if selected_zone != "Toutes" and 'Zone' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['Zone'] == selected_zone]
            if selected_cat and 'Catégorie' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['Catégorie'].isin(selected_cat)]

        # --- Contenu Principal ---
        if menu == "Dashboard":
            st.title(f"Dashboard Commercial - {city}")
            st.markdown("Vue d'ensemble de l'activité et de la distribution des points de vente.")
            
            # Metrics Row
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                metric_card("Points de Vente Total", f"{len(filtered_df):,}")
            with col2:
                formel = len(filtered_df[filtered_df['Statut']=='Formel'])
                pct = (formel/len(filtered_df)*100) if len(filtered_df)>0 else 0
                metric_card("Taux de Formalité", f"{pct:.1f}%")
            with col3:
                metric_card("Quartiers Couverts", filtered_df['Zone'].nunique())
            with col4:
                metric_card("Catégories Uniques", filtered_df['Catégorie'].nunique())

            st.markdown("### 📈 Analyse Détaillée")
            
            # Charts Row 1
            c1, c2 = st.columns([2, 1])
            with c1:
                with st.container(border=True):
                    st.subheader("Distribution par Catégorie")
                    counts = filtered_df['Catégorie'].value_counts().reset_index()
                    counts.columns = ['Catégorie', 'Nombre']
                    fig_bar = px.bar(
                        counts,
                        x='Catégorie', y='Nombre',
                        labels={'Catégorie': 'Catégorie', 'Nombre': 'Nombre'},
                        color='Catégorie',
                        color_discrete_sequence=['#ff6b6b', '#4ecdc4', '#45b7d1', '#f9ca24', '#a55eea', '#f39c12', '#95afc0']
                    )
                    fig_bar.update_layout(xaxis_title="", yaxis_title="Points de vente", showlegend=False, margin=dict(t=0, l=0, r=0, b=0), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(family="Space Grotesk"))
                    st.plotly_chart(fig_bar, use_container_width=True)
            
            with c2:
                with st.container(border=True):
                    st.subheader("Répartition Formel/Informel")
                    fig_pie = px.pie(
                        filtered_df, names='Statut', 
                        color='Statut',
                        color_discrete_map={'Formel':'#10b981', 'Informel':'#ef4444'},
                        hole=0.6
                    )
                    fig_pie.update_layout(showlegend=False, margin=dict(t=0, l=0, r=0, b=0), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(family="Space Grotesk"))
                    st.plotly_chart(fig_pie, use_container_width=True)

        elif menu == "Explorateur de Données":
            st.title("🗃️ Explorateur Données")
            st.markdown(f"Consultez et gérez la base de données de {city}. {len(filtered_df)} entrées affichées.")

            # Table "Shadcn-like" avec st.dataframe et Column Config
            st.dataframe(
                filtered_df,
                use_container_width=True,
                column_config={
                    "Image": st.column_config.ImageColumn("Aperçu"),
                    "Nom": st.column_config.TextColumn("Nom Commercial", width="medium"),
                    "Catégorie": st.column_config.TextColumn("Catégorie", width="medium"),
                    "Statut": st.column_config.TextColumn("Statut", width="small"),
                    "Score": st.column_config.ProgressColumn("Score Fiabilité", min_value=0, max_value=100, format="%d%%"),
                    "Latitude": st.column_config.NumberColumn("Lat", format="%.4f"),
                    "Longitude": st.column_config.NumberColumn("Lon", format="%.4f"),
                },
                height=600,
                hide_index=True 
            )

        elif menu == "Carte Interactive":
            st.title("🗺️ Géolocalisation")
            st.markdown("Carte interactive des points de vente.")
            
            if not filtered_df.empty:
               st.map(filtered_df, latitude='Latitude', longitude='Longitude', size=20, color='#2a7ae2')
            else:
               st.info("Aucune donnée géographique disponible pour ces filtres.")
        
        elif menu == "🧪 Labo - Scraping":
            import sys
            sys.path.append('.')
            
            from morocco_zones_config import get_all_zones, REGIONS, CITIES
            from scraping_orchestrator import ScrapingOrchestrator
            from data_manager import get_global_stats, get_all_zones_history
            
            st.title("🧪 Laboratoire de Scraping")
            st.markdown("Gérez le scraping des données de points de vente pour tout le Maroc.")
            
            # Onglets
            tab1, tab2, tab3 = st.tabs(["🚀 Scraping", "📊 Historique", "⚙️ Configuration"])
            
            with tab1:
                st.subheader("Lancer un scraping")
                
                # Type de scraping
                scraping_mode = st.radio(
                    "Mode de scraping",
                    ["Sélection personnalisée", "Toutes les régions", "Toutes les villes", "Tout le Maroc"],
                    horizontal=True
                )
                
                selected_zones = []
                
                if scraping_mode == "Sélection personnalisée":
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**📍 Régions**")
                        selected_regions = st.multiselect(
                            "Sélectionner les régions",
                            options=list(REGIONS.keys()),
                            label_visibility="collapsed"
                        )
                        selected_zones.extend([f"Région: {r}" for r in selected_regions])
                    
                    with col2:
                        st.markdown("**🏙️ Villes**")
                        selected_cities = st.multiselect(
                            "Sélectionner les villes",
                            options=list(CITIES.keys()),
                            label_visibility="collapsed"
                        )
                        selected_zones.extend([f"Ville: {c}" for c in selected_cities])
                
                elif scraping_mode == "Toutes les régions":
                    selected_zones = [f"Région: {r}" for r in REGIONS.keys()]
                    st.info(f"✅ {len(selected_zones)} régions sélectionnées")
                
                elif scraping_mode == "Toutes les villes":
                    selected_zones = [f"Ville: {c}" for c in CITIES.keys()]
                    st.info(f"✅ {len(selected_zones)} villes sélectionnées")
                
                elif scraping_mode == "Tout le Maroc":
                    selected_zones = [f"Région: {r}" for r in REGIONS.keys()]
                    st.info(f"✅ Scraping complet du Maroc ({len(selected_zones)} régions)")
                
                # Paramètres avancés
                with st.expander("⚙️ Paramètres avancés"):
                    col_dup1, col_dup2 = st.columns(2)
                    
                    with col_dup1:
                        st.markdown("**🧹 Détection de doublons**")
                        detection_mode = st.radio(
                            "Mode",
                            ["⚡ Rapide (sans nettoyage)", "🎯 Standard (optimisé)", "🔍 Complet (lent)"],
                            help="""
                            ⚡ Rapide : Pas de détection de doublons (~30s/ville)
                            🎯 Standard : Grille spatiale optimisée (~1-2min/ville) [RECOMMANDÉ]
                            🔍 Complet : Comparaison exhaustive (~13min/ville)
                            """,
                            index=1  # Standard par défaut
                        )
                    
                    with col_dup2:
                        st.markdown("**🔧 Stratégie de fusion**")
                        duplicate_strategy = st.selectbox(
                            "Stratégie de fusion",
                            ["keep_best", "keep_first", "keep_osm", "keep_atp"],
                            help="""
                            • keep_best: Garde l'entrée la plus complète
                            • keep_first: Garde la première occurrence
                            • keep_osm: Priorité aux données OSM
                            • keep_atp: Priorité aux données ATP
                            """,
                            label_visibility="visible"
                        )
                        st.caption("""\
                        • keep_best : privilégie la fiche la plus riche (téléphone, horaires, adresse)
                        • keep_first : conserve la première entrée rencontrée (ne modifie pas l'historique)
                        • keep_osm : si conflit, on garde la version OpenStreetMap
                        • keep_atp : si conflit, on garde la version ATP (sites officiels enseignes)
                        """)
                    
                    # Affichage des estimations
                    st.markdown("---")
                    estimated_time = {
                        "⚡ Rapide (sans nettoyage)": 0.5,
                        "🎯 Standard (optimisé)": 1.5,
                        "🔍 Complet (lent)": 13
                    }[detection_mode]
                    
                    total_estimated = estimated_time * len(selected_zones)
                    
                    col_est1, col_est2 = st.columns(2)
                    col_est1.metric("⏱️ Temps estimé/zone", f"{estimated_time:.1f} min")
                    col_est2.metric("⏱️ Temps total estimé", f"{total_estimated:.1f} min")
                    
                    show_logs = st.checkbox("Afficher les logs détaillés", value=True)
                
                # Bouton de lancement
                st.markdown("---")
                col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
                
                with col_btn1:
                    start_scraping = st.button("🚀 Lancer le scraping", type="primary", use_container_width=True, disabled=len(selected_zones) == 0)
                
                with col_btn2:
                    if st.button("🔄 Rafraîchir", use_container_width=True):
                        st.rerun()
                
                # Zone de scraping
                if start_scraping and selected_zones:
                    st.markdown("---")
                    
                    # Utiliser st.status pour les mises à jour en temps réel
                    with st.status(f"🔄 Scraping de {len(selected_zones)} zone(s)...", expanded=True) as status:
                        # Métriques en temps réel
                        metrics_container = st.empty()
                        
                        # État de progression
                        progress_state = {
                            'current': 0,
                            'total': len(selected_zones),
                            'points': 0,
                            'zones_done': []
                        }
                        
                        def update_metrics():
                            with metrics_container.container():
                                col1, col2, col3 = st.columns(3)
                                col1.metric("🎯 Zones", f"{progress_state['current']}/{progress_state['total']}")
                                col2.metric("📊 Points", progress_state['points'])
                                col3.metric("✅ Terminées", len(progress_state['zones_done']))
                        
                        # Callbacks
                        def progress_callback(current, total, message):
                            progress_state['current'] = current
                            progress_state['total'] = total
                            st.write(f"⏳ **{current}/{total}** - {message}")
                            update_metrics()
                        
                        def log_callback(message, level):
                            if level in ['INFO', 'SUCCESS']:
                                if 'points collectés' in message.lower():
                                    try:
                                        points = int(message.split()[0])
                                        progress_state['points'] += points
                                        update_metrics()
                                    except:
                                        pass
                                st.write(f"💬 {message}")
                        
                        # Orchestrateur
                        orchestrator = ScrapingOrchestrator(verbose=True)
                        orchestrator.set_progress_callback(progress_callback)
                        orchestrator.set_log_callback(log_callback)
                        
                        # Déterminer le mode de scraping
                        skip_duplicates = (detection_mode == "⚡ Rapide (sans nettoyage)")
                        use_spatial_optimization = (detection_mode == "🎯 Standard (optimisé)")
                        
                        if skip_duplicates:
                            st.write("⚡ **Mode rapide activé** - Pas de détection de doublons")
                        elif use_spatial_optimization:
                            st.write("🎯 **Mode optimisé activé** - Grille spatiale (7x plus rapide)")
                        else:
                            st.write("🔍 **Mode complet activé** - Comparaison exhaustive")
                        
                        # Lancer le scraping
                        import time
                        start_time = time.time()
                        
                        st.write("🚀 **Démarrage du scraping...**")
                        update_metrics()
                        
                        summary = orchestrator.scrape_multiple_zones(
                            selected_zones, 
                            duplicate_strategy,
                            skip_duplicates=skip_duplicates
                        )
                        
                        elapsed_time = time.time() - start_time
                        
                        # Mise à jour finale
                        status.update(label=f"✅ Scraping terminé en {elapsed_time:.1f}s!", state="complete")
                    
                    
                    # Résultats finaux
                    st.markdown("---")
                    st.subheader("📊 Résultats du scraping")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("✅ Zones réussies", summary['success_count'])
                    with col2:
                        st.metric("📊 Points collectés", summary['total_points'])
                    with col3:
                        st.metric("❌ Erreurs", summary['error_count'])
                    with col4:
                        st.metric("⏱️ Durée", f"{elapsed_time:.1f}s")
                    
                    # Tableau des résultats
                    if summary['results']:
                        st.markdown("### 📊 Détails par zone")
                        results_df = orchestrator.get_results_dataframe()
                        st.dataframe(results_df, use_container_width=True)
                    
                    # Erreurs
                    if summary['errors']:
                        st.markdown("### ⚠️ Erreurs rencontrées")
                        for error in summary['errors']:
                            st.error(f"**{error['zone']}**: {error['error']}")
            
            with tab2:
                st.subheader("📜 Historique des scrapings")
                
                try:
                    # Statistiques globales
                    global_stats = get_global_stats()
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Zones scrapées", global_stats['total_zones'])
                    with col2:
                        st.metric("Points totaux", global_stats['total_points'])
                    with col3:
                        st.metric("Mises à jour", global_stats['total_updates'])
                    
                    st.markdown("---")
                    
                    # Historique détaillé
                    all_histories = get_all_zones_history()
                    
                    if all_histories:
                        st.markdown("### 📋 Historique par zone")
                        
                        for history in all_histories:
                            with st.expander(f"🗺️ {history['zone']} ({len(history['updates'])} mises à jour)"):
                                st.json(history)
                    else:
                        st.info("Aucun historique disponible. Lancez un scraping pour commencer.")
                
                except Exception as e:
                    st.error(f"Erreur lors du chargement de l'historique: {e}")
            
            with tab3:
                st.subheader("⚙️ Configuration")
                
                st.markdown("### 📍 Zones disponibles")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Régions administratives**")
                    st.info(f"{len(REGIONS)} régions configurées")
                    for region_name in REGIONS.keys():
                        st.text(f"• {region_name}")
                
                with col2:
                    st.markdown("**Grandes villes**")
                    st.info(f"{len(CITIES)} villes configurées")
                    for city_name in list(CITIES.keys())[:15]:  # Afficher les 15 premières
                        st.text(f"• {city_name}")
                    if len(CITIES) > 15:
                        st.text(f"... et {len(CITIES) - 15} autres")
                
                st.markdown("---")
                st.markdown("### 🔧 Paramètres de scraping")
                
                from morocco_zones_config import SCRAPING_CONFIG
                st.json(SCRAPING_CONFIG)
                
                st.markdown("---")
                st.markdown("### 📂 Structure des fichiers")
                st.code("""
data/          # Fichiers CSV des points de vente
logs/          # Logs de scraping
backups/       # Backups automatiques
history/       # Historique JSON des mises à jour
                """)
               
    elif st.session_state["authentication_status"] is False:
        st.error('Username/password incorrect')
    elif st.session_state["authentication_status"] is None:
        st.warning('Veuillez vous connecter pour accéder à la plateforme.')

if __name__ == "__main__":
    main()

