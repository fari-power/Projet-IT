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
    
</style>
""", unsafe_allow_html=True)

# --- Fonction de chargement des données ---
@st.cache_data
def load_data():
    try:
        # Essayer de charger le fichier Marrakech, sinon fallback sur Casablanca ou Fès
        if pd.io.common.file_exists("points_vente_marrakech_complet.csv"):
             df = pd.read_csv("points_vente_marrakech_complet.csv")
             city = "Marrakech"
        elif pd.io.common.file_exists("points_vente_fes_complet.csv"):
             df = pd.read_csv("points_vente_fes_complet.csv")
             city = "Fès"
        elif pd.io.common.file_exists("points_vente_rabat_complet.csv"):
             df = pd.read_csv("points_vente_rabat_complet.csv")
             city = "Rabat"
        else:
             df = pd.read_csv("points_vente_casablanca_complet.csv")
             city = "Casablanca"
        
        # Nettoyage basique
        if 'Latitude' in df.columns:
            df = df.dropna(subset=['Latitude', 'Longitude'])
        return df, city
    except Exception as e:
        st.error(f"Erreur de chargement: {e}")
        return pd.DataFrame(), "Erreur"

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
            menu = st.radio("Navigation", ["Dashboard", "Explorateur de Données", "Carte Interactive", "Paramètres"], label_visibility="collapsed")
            
            st.markdown("### Filtres Globaux")
            df, city = load_data()
            
            selected_zone = st.selectbox("Zone", ["Toutes"] + sorted(df['Zone'].dropna().unique().tolist()))
            selected_cat = st.multiselect("Catégories", sorted(df['Catégorie'].unique().tolist()), default=[])
            
            st.markdown("---")
            authenticator.logout('Déconnexion', 'sidebar')

        # Filtrage
        filtered_df = df.copy()
        if selected_zone != "Toutes":
            filtered_df = filtered_df[filtered_df['Zone'] == selected_zone]
        if selected_cat:
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
                st.markdown('<div class="metric-container" style="height: 100%;">', unsafe_allow_html=True)
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
                fig_bar.update_layout(xaxis_title="", yaxis_title="Points de vente", showlegend=False, margin=dict(t=0, l=0, r=0, b=0))
                st.plotly_chart(fig_bar, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            with c2:
                st.markdown('<div class="metric-container" style="height: 100%;">', unsafe_allow_html=True)
                st.subheader("Répartition Formel/Informel")
                fig_pie = px.pie(
                    filtered_df, names='Statut', 
                    color='Statut',
                    color_discrete_map={'Formel':'#10b981', 'Informel':'#ef4444'},
                    hole=0.6
                )
                fig_pie.update_layout(showlegend=False, margin=dict(t=0, l=0, r=0, b=0))
                st.plotly_chart(fig_pie, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

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
               
    elif st.session_state["authentication_status"] is False:
        st.error('Username/password incorrect')
    elif st.session_state["authentication_status"] is None:
        st.warning('Veuillez vous connecter pour accéder à la plateforme.')

if __name__ == "__main__":
    main()
