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
def get_available_data_files():
    """Liste tous les fichiers CSV disponibles dans le dossier data/"""
    from pathlib import Path
    
    data_dir = Path("data")
    if not data_dir.exists():
        return []
    
    csv_files = list(data_dir.glob("points_vente_*_complet.csv"))
    
    # Extraire les noms propres (ville/région) depuis les noms de fichiers
    file_info = []
    for file in csv_files:
        zone_name = file.stem.replace("points_vente_", "").replace("_complet", "")
        # Capitaliser et remplacer les tirets par espaces pour l'affichage
        display_name = zone_name.replace("-", " ").title()
        file_info.append({
            'file': file,
            'zone_name': zone_name,
            'display_name': display_name
        })
    
    return file_info

@st.cache_data
def load_selected_data(selected_option):
    """Charge les données selon la sélection: une zone spécifique ou toutes les zones"""
    from pathlib import Path
    
    file_info_list = get_available_data_files()
    
    if not file_info_list:
        empty_df = pd.DataFrame(columns=['Nom', 'Catégorie', 'Latitude', 'Longitude', 'Zone', 'Statut'])
        return empty_df, "Aucune donnée"
    
    try:
        if selected_option == "🌍 Toutes les zones":
            # Charger et concaténer tous les fichiers
            all_dfs = []
            for file_info in file_info_list:
                df = pd.read_csv(file_info['file'])
                # Ajouter colonne Zone si manquante
                if 'Zone' not in df.columns:
                    df['Zone'] = file_info['display_name']
                all_dfs.append(df)
            
            df = pd.concat(all_dfs, ignore_index=True)
            city_name = "Toutes les zones"
        else:
            # Charger le fichier sélectionné
            selected_file_info = next((f for f in file_info_list if f['display_name'] == selected_option), None)
            
            if not selected_file_info:
                empty_df = pd.DataFrame(columns=['Nom', 'Catégorie', 'Latitude', 'Longitude', 'Zone', 'Statut'])
                return empty_df, "Erreur"
            
            df = pd.read_csv(selected_file_info['file'])
            city_name = selected_file_info['display_name']
            
            # Ajouter colonne Zone si manquante
            if 'Zone' not in df.columns:
                df['Zone'] = city_name
        
        # Nettoyage basique
        if 'Latitude' in df.columns:
            df = df.dropna(subset=['Latitude', 'Longitude'])
        
        return df, city_name
        
    except Exception as e:
        st.error(f"Erreur de chargement: {e}")
        empty_df = pd.DataFrame(columns=['Nom', 'Catégorie', 'Latitude', 'Longitude', 'Zone', 'Statut'])
        return empty_df, "Erreur"

@st.cache_data
def load_data():
    """Fonction de compatibilité - charge les données par défaut (toutes les zones)"""
    return load_selected_data("🌍 Toutes les zones")

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
            menu = st.radio("Navigation", ["Dashboard", "Explorateur de Données", "Carte Interactive", "🧪 Labo - Scraping"], label_visibility="collapsed")
            
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
            st.title("📊 Dashboard Commercial")
            st.markdown("Vue d'ensemble de l'activité et de la distribution des points de vente.")
            
            # Sélecteur de zone/fichier pour le Dashboard
            available_files = get_available_data_files()
            
            if available_files:
                file_options = ["🌍 Toutes les zones"] + [f['display_name'] for f in available_files]
                
                col_selector1, col_selector2 = st.columns([2, 3])
                with col_selector1:
                    selected_data_source = st.selectbox(
                        "📍 Sélectionner la zone à analyser",
                        file_options,
                        index=0,
                        help="Choisissez une zone spécifique (ville ou région) ou affichez toutes les données agrégées"
                    )
                
                with col_selector2:
                    st.info(f"📊 **{len(available_files)} zone(s) disponible(s)** - Scraping via le Labo")
                
                st.markdown("---")
                
                # Charger les données selon la sélection
                dashboard_df, dashboard_city = load_selected_data(selected_data_source)
                
                # Appliquer les filtres globaux (sidebar)
                dashboard_filtered = dashboard_df.copy()
                if not dashboard_df.empty:
                    if selected_zone != "Toutes" and 'Zone' in dashboard_filtered.columns:
                        dashboard_filtered = dashboard_filtered[dashboard_filtered['Zone'] == selected_zone]
                    if selected_cat and 'Catégorie' in dashboard_filtered.columns:
                        dashboard_filtered = dashboard_filtered[dashboard_filtered['Catégorie'].isin(selected_cat)]
                
                filtered_df = dashboard_filtered
                city = dashboard_city
            else:
                st.warning("🔍 Aucune donnée disponible. Lancez un scraping dans '🧪 Labo - Scraping' pour générer des données.")
                filtered_df = pd.DataFrame(columns=['Nom', 'Catégorie', 'Latitude', 'Longitude', 'Zone', 'Statut'])
                city = "Aucune donnée"
            
            if not filtered_df.empty:
                # Metrics Row
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    metric_card("Points de Vente Total", f"{len(filtered_df):,}")
                with col2:
                    formel = len(filtered_df[filtered_df['Statut']=='Formel']) if 'Statut' in filtered_df.columns else 0
                    pct = (formel/len(filtered_df)*100) if len(filtered_df)>0 else 0
                    metric_card("Taux de Formalité", f"{pct:.1f}%")
                with col3:
                    metric_card("Zones Couvertes", filtered_df['Zone'].nunique() if 'Zone' in filtered_df.columns else 0)
                with col4:
                    metric_card("Catégories", filtered_df['Catégorie'].nunique() if 'Catégorie' in filtered_df.columns else 0)

                st.markdown("---")
                st.markdown("### 📈 Analyse Détaillée")
                
                # Charts Row 1
                c1, c2 = st.columns([2, 1])
                with c1:
                    with st.container(border=True):
                        st.subheader("📊 Distribution par Catégorie")
                        if 'Catégorie' in filtered_df.columns:
                            counts = filtered_df['Catégorie'].value_counts().head(10).reset_index()
                            counts.columns = ['Catégorie', 'Nombre']
                            fig_bar = px.bar(
                                counts,
                                x='Catégorie', y='Nombre',
                                labels={'Catégorie': 'Catégorie', 'Nombre': 'Nombre'},
                                color='Nombre',
                                color_continuous_scale='Blues',
                                text='Nombre'
                            )
                            fig_bar.update_traces(textposition='outside')
                            fig_bar.update_layout(
                                xaxis_title="", 
                                yaxis_title="Points de vente", 
                                showlegend=False, 
                                margin=dict(t=10, l=0, r=0, b=0),
                                plot_bgcolor='rgba(0,0,0,0)',
                                paper_bgcolor='rgba(0,0,0,0)',
                                font=dict(family="Space Grotesk", size=12),
                                xaxis={'categoryorder':'total descending'}
                            )
                            st.plotly_chart(fig_bar, use_container_width=True)
                        else:
                            st.info("Colonne 'Catégorie' manquante")
                
                with c2:
                    with st.container(border=True):
                        st.subheader("🎯 Formel vs Informel")
                        if 'Statut' in filtered_df.columns:
                            statut_counts = filtered_df['Statut'].value_counts()
                            fig_pie = px.pie(
                                values=statut_counts.values,
                                names=statut_counts.index,
                                color=statut_counts.index,
                                color_discrete_map={'Formel':'#10b981', 'Informel':'#ef4444'},
                                hole=0.65
                            )
                            fig_pie.update_traces(
                                textposition='inside',
                                textinfo='percent+label',
                                textfont_size=14
                            )
                            fig_pie.update_layout(
                                showlegend=False,
                                margin=dict(t=10, l=0, r=0, b=0),
                                plot_bgcolor='rgba(0,0,0,0)',
                                paper_bgcolor='rgba(0,0,0,0)',
                                font=dict(family="Space Grotesk")
                            )
                            st.plotly_chart(fig_pie, use_container_width=True)
                            
                            # Stats textuelles
                            st.markdown(f"**Formel:** {statut_counts.get('Formel', 0):,} ({pct:.1f}%)")
                            st.markdown(f"**Informel:** {statut_counts.get('Informel', 0):,} ({100-pct:.1f}%)")
                        else:
                            st.info("Colonne 'Statut' manquante")
                
                # Charts Row 2
                st.markdown("---")
                c3, c4 = st.columns(2)
                
                with c3:
                    with st.container(border=True):
                        st.subheader("🗺️ Top 10 Zones")
                        if 'Zone' in filtered_df.columns:
                            zone_counts = filtered_df['Zone'].value_counts().head(10).reset_index()
                            zone_counts.columns = ['Zone', 'Nombre']
                            fig_zones = px.bar(
                                zone_counts,
                                y='Zone', x='Nombre',
                                orientation='h',
                                color='Nombre',
                                color_continuous_scale='Viridis',
                                text='Nombre'
                            )
                            fig_zones.update_traces(textposition='outside')
                            fig_zones.update_layout(
                                xaxis_title="Nombre de points",
                                yaxis_title="",
                                showlegend=False,
                                margin=dict(t=10, l=0, r=0, b=0),
                                plot_bgcolor='rgba(0,0,0,0)',
                                paper_bgcolor='rgba(0,0,0,0)',
                                font=dict(family="Space Grotesk"),
                                yaxis={'categoryorder':'total ascending'},
                                height=400
                            )
                            st.plotly_chart(fig_zones, use_container_width=True)
                        else:
                            st.info("Colonne 'Zone' manquante")
                
                with c4:
                    with st.container(border=True):
                        st.subheader("📋 Statistiques Détaillées")
                        
                        # Densité
                        if 'Zone' in filtered_df.columns and filtered_df['Zone'].nunique() > 0:
                            avg_per_zone = len(filtered_df) / filtered_df['Zone'].nunique()
                            st.metric("Densité moyenne", f"{avg_per_zone:.1f} points/zone")
                        
                        # Top catégorie
                        if 'Catégorie' in filtered_df.columns:
                            top_cat = filtered_df['Catégorie'].value_counts().index[0]
                            top_cat_count = filtered_df['Catégorie'].value_counts().values[0]
                            st.metric("Top Catégorie", top_cat, f"{top_cat_count} points")
                        
                        # Complétude des données
                        if len(filtered_df) > 0:
                            completeness = (1 - filtered_df.isnull().sum().sum() / (len(filtered_df) * len(filtered_df.columns))) * 100
                            st.metric("Complétude des données", f"{completeness:.1f}%")
                        
                        st.markdown("---")
                        
                        # Tableau récapitulatif
                        st.markdown("**📊 Résumé par Statut et Catégorie**")
                        if 'Statut' in filtered_df.columns and 'Catégorie' in filtered_df.columns:
                            pivot = pd.crosstab(
                                filtered_df['Catégorie'],
                                filtered_df['Statut'],
                                margins=True,
                                margins_name="Total"
                            ).head(8)
                            st.dataframe(pivot, use_container_width=True)

        elif menu == "Explorateur de Données":
            st.title("🗃️ Explorateur de Données")
            st.markdown(f"Base de données complète de **{city}**")

            if filtered_df.empty:
                st.warning("🔍 Aucune donnée disponible. Lancez un scraping dans '🧪 Labo - Scraping'")
            else:
                # Barre de recherche et filtres avancés
                col_search, col_export = st.columns([3, 1])
                
                with col_search:
                    search_term = st.text_input(
                        "🔍 Rechercher",
                        placeholder="Nom du commerce, adresse, catégorie...",
                        label_visibility="collapsed"
                    )
                
                with col_export:
                    st.download_button(
                        label="📥 Exporter CSV",
                        data=filtered_df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig'),
                        file_name=f"export_{city}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                
                # Filtrage par recherche
                if search_term:
                    mask = filtered_df.apply(lambda row: row.astype(str).str.contains(search_term, case=False).any(), axis=1)
                    display_df = filtered_df[mask]
                    st.info(f"🔎 {len(display_df)} résultat(s) trouvé(s) pour '{search_term}'")
                else:
                    display_df = filtered_df
                
                # Statistiques rapides
                col_stat1, col_stat2, col_stat3 = st.columns(3)
                col_stat1.metric("📊 Entrées affichées", f"{len(display_df):,}")
                col_stat2.metric("📂 Total base", f"{len(df):,}")
                col_stat3.metric("🔍 Filtré", f"{len(filtered_df):,}")
                
                st.markdown("---")
                
                # Configuration des colonnes pour un affichage optimal
                column_config = {
                    "Nom": st.column_config.TextColumn("🏪 Nom Commercial", width="large"),
                    "Catégorie": st.column_config.TextColumn("📦 Catégorie", width="medium"),
                    "Statut": st.column_config.TextColumn("⚖️ Statut", width="small"),
                    "Zone": st.column_config.TextColumn("📍 Zone", width="medium"),
                    "Latitude": st.column_config.NumberColumn("📐 Lat", format="%.5f"),
                    "Longitude": st.column_config.NumberColumn("📐 Lon", format="%.5f"),
                }
                
                # Ajouter les colonnes si elles existent
                if "Adresse" in display_df.columns:
                    column_config["Adresse"] = st.column_config.TextColumn("🏠 Adresse", width="large")
                if "Source" in display_df.columns:
                    column_config["Source"] = st.column_config.TextColumn("🔗 Source", width="small")
                if "Image" in display_df.columns:
                    column_config["Image"] = st.column_config.ImageColumn("🖼️ Image", width="small")
                
                # Table interactive
                st.dataframe(
                    display_df,
                    use_container_width=True,
                    column_config=column_config,
                    height=600,
                    hide_index=True
                )
                
                # Détails sélectionnés (optionnel - si on veut permettre la sélection)
                with st.expander("ℹ️ Informations complémentaires"):
                    st.markdown(f"""
                    **📊 Résumé des données :**
                    - Total des entrées : **{len(df):,}**
                    - Entrées filtrées : **{len(filtered_df):,}**
                    - Entrées affichées : **{len(display_df):,}**
                    - Colonnes disponibles : **{len(display_df.columns)}**
                    - Complétude : **{(1 - display_df.isnull().sum().sum() / (len(display_df) * len(display_df.columns)) if len(display_df) > 0 else 0) * 100:.1f}%**
                    """)
                    
                    if st.checkbox("Afficher les statistiques détaillées"):
                        st.write("**📈 Statistiques par colonne :**")
                        st.write(display_df.describe(include='all'))

        elif menu == "Carte Interactive":
            st.title("🗺️ Carte Interactive")
            st.markdown(f"Visualisation géographique des points de vente de **{city}**")
            
            if filtered_df.empty:
                st.warning("🔍 Aucune donnée disponible pour afficher la carte.")
            else:
                # Filtres de la carte
                col_map1, col_map2 = st.columns(2)
                
                with col_map1:
                    show_clusters = st.checkbox("🔵 Activer le clustering", value=True, help="Regrouper les points proches")
                
                with col_map2:
                    color_by = st.selectbox(
                        "🎨 Coloration",
                        options=["Catégorie", "Statut", "Zone", "Uniforme"],
                        index=0
                    )
                
                # Préparer les données pour la carte
                map_df = filtered_df.copy()
                if 'Latitude' in map_df.columns and 'Longitude' in map_df.columns:
                    map_df = map_df.dropna(subset=['Latitude', 'Longitude'])
                
                if map_df.empty:
                    st.error("❌ Aucune coordonnée GPS valide dans les données filtrées")
                else:
                    # Créer une carte Plotly avec clustering visuel
                    # Assigner des couleurs selon la sélection
                    if color_by == "Uniforme":
                        map_df['color_group'] = "Point de vente"
                        color_discrete_map = {"Point de vente": "#3b82f6"}
                    elif color_by in map_df.columns:
                        map_df['color_group'] = map_df[color_by].fillna("Non spécifié")
                        color_discrete_map = None
                    else:
                        map_df['color_group'] = "Point de vente"
                        color_discrete_map = {"Point de vente": "#3b82f6"}
                    
                    # Créer le texte de hover personnalisé
                    if 'Nom' in map_df.columns:
                        map_df['hover_text'] = map_df.apply(
                            lambda row: f"<b>{row.get('Nom', 'N/A')}</b><br>" +
                                       f"📦 {row.get('Catégorie', 'N/A')}<br>" +
                                       f"📍 {row.get('Zone', 'N/A')}<br>" +
                                       f"⚖️ {row.get('Statut', 'N/A')}",
                            axis=1
                        )
                    else:
                        map_df['hover_text'] = "Point de vente"
                    
                    # Créer la carte scatter
                    fig = px.scatter_mapbox(
                        map_df,
                        lat="Latitude",
                        lon="Longitude",
                        color="color_group",
                        color_discrete_map=color_discrete_map,
                        hover_name="hover_text" if 'hover_text' in map_df.columns else None,
                        zoom=11,
                        height=700,
                        title=f"Carte des {len(map_df)} points de vente"
                    )
                    
                    # Configurer le style de la carte
                    fig.update_layout(
                        mapbox_style="open-street-map",
                        margin={"r": 0, "t": 40, "l": 0, "b": 0},
                        legend=dict(
                            orientation="v",
                            yanchor="top",
                            y=0.99,
                            xanchor="right",
                            x=0.99,
                            bgcolor="rgba(255, 255, 255, 0.8)"
                        )
                    )
                    
                    # Ajuster les marqueurs
                    fig.update_traces(
                        marker=dict(size=8, opacity=0.7),
                        hovertemplate='%{hovertext}<extra></extra>'
                    )
                    
                    # Afficher la carte
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Statistiques de la carte
                    col_map_stat1, col_map_stat2, col_map_stat3 = st.columns(3)
                    col_map_stat1.metric("📍 Points affichés", f"{len(map_df):,}")
                    
                    if 'Zone' in map_df.columns:
                        col_map_stat2.metric("🗺️ Zones couvertes", map_df['Zone'].nunique())
                    
                    # Calculer la densité (points/km²)
                    if len(map_df) > 1:
                        from math import radians, cos, sin, asin, sqrt
                        lat_range = map_df['Latitude'].max() - map_df['Latitude'].min()
                        lon_range = map_df['Longitude'].max() - map_df['Longitude'].min()
                        
                        # Approximation de la surface en km² (1° ≈ 111 km en latitude)
                        approx_area = lat_range * lon_range * 111 * 111 * cos(radians(map_df['Latitude'].mean()))
                        if approx_area > 0:
                            density = len(map_df) / approx_area
                            col_map_stat3.metric("🔥 Densité", f"{density:.1f} pts/km²")
                    
                    # Légende interactive
                    with st.expander("📖 Légende et filtres avancés"):
                        st.markdown(f"""
                        **🎨 Code couleur actuel :** {color_by}
                        
                        **🔵 Clustering :** {'Activé' if show_clusters else 'Désactivé'}
                        
                        **📊 Conseils d'utilisation :**
                        - Zoom : Molette de la souris ou pincement tactile
                        - Déplacement : Cliquer-glisser sur la carte
                        - Hover : Survoler un point pour voir les détails
                        - Plein écran : Icône dans le coin supérieur droit
                        """)
                        
                        if color_by != "Uniforme" and color_by in map_df.columns:
                            st.write(f"**Répartition par {color_by} :**")
                            distribution = map_df[color_by].value_counts()
                            st.bar_chart(distribution)
        
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

