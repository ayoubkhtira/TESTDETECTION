import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import time
import json
import os

# Configuration de base
st.set_page_config(
    page_title="VisionGuard AI",
    page_icon="👁️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS simple
st.markdown("""
<style>
    .main-title {
        text-align: center;
        padding: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 30px;
    }
    .metric-card {
        background: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
        margin-bottom: 15px;
    }
    .sidebar-content {
        background: linear-gradient(180deg, #2c3e50 0%, #1a1a2e 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
    }
    .status-badge {
        display: inline-block;
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: bold;
        margin: 5px;
    }
    .status-online {
        background-color: #4CAF50;
        color: white;
    }
    .status-offline {
        background-color: #ff6b6b;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Initialisation des données
if 'detections' not in st.session_state:
    st.session_state.detections = []
if 'stats' not in st.session_state:
    st.session_state.stats = {
        'person': 0,
        'phone': 0,
        'alert': 0
    }
if 'history' not in st.session_state:
    st.session_state.history = []

# Titre principal
st.markdown("""
<div class="main-title">
    <h1>👁️ VisionGuard AI</h1>
    <p>Système de surveillance simplifié et stable</p>
</div>
""", unsafe_allow_html=True)

# Barre latérale
with st.sidebar:
    st.markdown("<div class='sidebar-content'>", unsafe_allow_html=True)
    
    st.markdown("### ⚙️ Configuration")
    
    # Mode de fonctionnement
    mode = st.radio(
        "Mode d'opération",
        ["🔴 Simulation", "🟢 Mode réel (si disponible)"],
        index=0
    )
    
    st.markdown("---")
    
    # Paramètres
    st.markdown("### 📊 Paramètres")
    
    sensitivity = st.slider(
        "Sensibilité de détection",
        min_value=1, max_value=10, value=5
    )
    
    alert_threshold = st.slider(
        "Seuil d'alerte (téléphones)",
        min_value=1, max_value=10, value=3
    )
    
    st.markdown("---")
    
    # Télégram
    st.markdown("### 📱 Notifications")
    
    telegram_enabled = st.checkbox("Activer Telegram", value=False)
    
    if telegram_enabled:
        telegram_token = st.text_input("Token Telegram", type="password")
        chat_id = st.text_input("Chat ID")
    
    st.markdown("---")
    
    # Contrôles
    col1, col2 = st.columns(2)
    with col1:
        if st.button("▶️ Démarrer", type="primary", use_container_width=True):
            st.session_state.running = True
            st.rerun()
    
    with col2:
        if st.button("⏹️ Arrêter", use_container_width=True):
            st.session_state.running = False
            st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)

# Métriques principales
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
    st.metric("👥 Personnes", st.session_state.stats['person'], "+2")
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
    st.metric("📱 Téléphones", st.session_state.stats['phone'], "+1")
    st.markdown("</div>", unsafe_allow_html=True)

with col3:
    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
    alert_status = "🟢 Actif" if st.session_state.stats['alert'] == 0 else "🔴 Alerte"
    st.metric("🚨 Alertes", st.session_state.stats['alert'], alert_status)
    st.markdown("</div>", unsafe_allow_html=True)

with col4:
    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
    status = "🟢 En ligne" if st.session_state.get('running', False) else "🔴 Hors ligne"
    st.metric("État système", status)
    st.markdown("</div>", unsafe_allow_html=True)

# Onglets
tab1, tab2, tab3 = st.tabs(["🎥 Surveillance", "📊 Statistiques", "📋 Historique"])

with tab1:
    st.markdown("### Flux de surveillance")
    
    # Zone de flux vidéo
    video_placeholder = st.empty()
    
    # Simuler un flux vidéo
    if st.session_state.get('running', False):
        # Afficher une simulation de flux
        video_placeholder.markdown("""
        <div style='background: black; border-radius: 10px; padding: 20px; text-align: center;'>
            <div style='color: white; font-size: 20px; margin-bottom: 20px;'>
                🎥 Flux de surveillance actif
            </div>
            <div style='display: inline-block; background: #333; padding: 30px; border-radius: 5px;'>
                <div style='font-size: 50px;'>📱</div>
            </div>
            <div style='color: #4CAF50; margin-top: 20px;'>
                Détection en cours...
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Simuler des détections
        if st.button("Simuler une détection"):
            import random
            detection = {
                "time": datetime.now().strftime("%H:%M:%S"),
                "type": random.choice(["Personne", "Téléphone", "Voiture", "Sac"]),
                "confidence": random.randint(70, 99),
                "location": f"Zone {random.randint(1, 4)}"
            }
            
            st.session_state.detections.append(detection)
            
            if detection["type"] == "Téléphone":
                st.session_state.stats['phone'] += 1
                st.session_state.stats['alert'] += 1
                
                # Ajouter à l'historique
                st.session_state.history.append({
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "event": "Détection téléphone",
                    "niveau": "⚠️ Moyen"
                })
                
                st.success(f"📱 Téléphone détecté à {detection['time']} avec {detection['confidence']}% de confiance")
                
            elif detection["type"] == "Personne":
                st.session_state.stats['person'] += 1
                st.info(f"👤 Personne détectée à {detection['time']}")
            
            st.rerun()
    else:
        video_placeholder.markdown("""
        <div style='background: #f0f2f6; border-radius: 10px; padding: 50px; text-align: center;'>
            <div style='font-size: 60px; margin-bottom: 20px;'>📹</div>
            <h3>Surveillance en pause</h3>
            <p>Cliquez sur "Démarrer" dans la barre latérale pour commencer</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Détections récentes
    st.markdown("### Détections récentes")
    
    if st.session_state.detections:
        recent_detections = st.session_state.detections[-5:]  # 5 dernières
        for det in reversed(recent_detections):
            st.write(f"**{det['time']}** - {det['type']} ({det['confidence']}%) - {det['location']}")
    else:
        st.info("Aucune détection récente")

with tab2:
    st.markdown("### Statistiques de détection")
    
    # Graphique simple avec données simulées
    chart_data = pd.DataFrame({
        'Heure': [f'{h}:00' for h in range(8, 18)],
        'Personnes': np.random.randint(0, 10, 10),
        'Téléphones': np.random.randint(0, 5, 10),
        'Autres': np.random.randint(0, 8, 10)
    })
    
    st.bar_chart(chart_data.set_index('Heure'))
    
    # Statistiques détaillées
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🔍 Vue d'ensemble")
        total_detections = len(st.session_state.detections)
        phone_detections = sum(1 for d in st.session_state.detections if d['type'] == 'Téléphone')
        person_detections = sum(1 for d in st.session_state.detections if d['type'] == 'Personne')
        
        st.metric("Détections totales", total_detections)
        st.metric("Téléphones détectés", phone_detections)
        st.metric("Personnes détectées", person_detections)
    
    with col2:
        st.markdown("#### 📈 Tendances")
        st.write("**Aujourd'hui:**")
        st.progress(0.75, "Activité de surveillance")
        st.progress(0.4, "Alertes déclenchées")
        st.progress(0.9, "Précision système")

with tab3:
    st.markdown("### Historique des événements")
    
    # Créer des données d'historique si vide
    if not st.session_state.history:
        sample_history = [
            {"timestamp": "2024-01-15 09:30:00", "event": "Système démarré", "niveau": "ℹ️ Info"},
            {"timestamp": "2024-01-15 10:15:00", "event": "Téléphone détecté", "niveau": "⚠️ Moyen"},
            {"timestamp": "2024-01-15 11:45:00", "event": "Personne détectée", "niveau": "ℹ️ Info"},
            {"timestamp": "2024-01-15 12:30:00", "event": "Alerte envoyée", "niveau": "🚨 Haute"},
            {"timestamp": "2024-01-15 14:20:00", "event": "Système mis à jour", "niveau": "ℹ️ Info"}
        ]
        st.session_state.history = sample_history
    
    # Afficher l'historique
    history_df = pd.DataFrame(st.session_state.history)
    st.dataframe(
        history_df,
        use_container_width=True,
        column_config={
            "timestamp": "Horodatage",
            "event": "Événement",
            "niveau": "Niveau"
        }
    )
    
    # Boutons d'export
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📥 Exporter CSV"):
            csv = history_df.to_csv(index=False)
            st.download_button(
                label="Télécharger",
                data=csv,
                file_name="historique_surveillance.csv",
                mime="text/csv"
            )
    
    with col2:
        if st.button("🗑️ Effacer l'historique"):
            st.session_state.history = []
            st.rerun()

# Zone d'information
st.markdown("---")
st.markdown("### ℹ️ Informations système")

info_col1, info_col2, info_col3 = st.columns(3)

with info_col1:
    st.markdown("**Version**")
    st.write("1.0.0")
    
    st.markdown("**Statut**")
    if st.session_state.get('running', False):
        st.markdown("<span class='status-badge status-online'>En ligne</span>", unsafe_allow_html=True)
    else:
        st.markdown("<span class='status-badge status-offline'>Hors ligne</span>", unsafe_allow_html=True)

with info_col2:
    st.markdown("**Dernière mise à jour**")
    st.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    st.markdown("**Détections aujourd'hui**")
    st.write(len(st.session_state.detections))

with info_col3:
    st.markdown("**Mode actuel**")
    st.write("Simulation" if mode == "🔴 Simulation" else "Réel")
    
    st.markdown("**Alertes actives**")
    st.write(st.session_state.stats['alert'])

# Instructions de configuration
with st.expander("🔧 Instructions de configuration"):
    st.markdown("""
    ### Pour Streamlit Cloud
    
    1. **Créer les fichiers suivants dans votre dépôt :**
    
    **requirements.txt :**
    ```
    streamlit==1.28.0
    pandas==2.1.0
    numpy==1.24.0
    ```
    
    2. **Structure du projet :**
    ```
    votre-repo/
    ├── app.py
    ├── requirements.txt
    └── README.md
    ```
    
    3. **Déployer sur Streamlit Cloud :**
       - Connectez-vous à Streamlit Cloud
       - Importez votre dépôt GitHub
       - Définissez le point d'entrée comme `app.py`
    
    ### Pour une version avec OpenCV
    
    Si vous voulez ajouter la détection vidéo réelle :
    
    **Modifiez requirements.txt :**
    ```
    streamlit==1.28.0
    pandas==2.1.0
    numpy==1.24.0
    opencv-python-headless==4.8.1.78
    ultralytics==8.0.0
    ```
    
    **Ajoutez packages.txt :**
    ```
    libgl1-mesa-glx
    libglib2.0-0
    libsm6
    libxext6
    libxrender1
    ```
    """)

# Pied de page
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666; padding: 20px;'>"
    "👁️ VisionGuard AI | Système de surveillance simplifié | v1.0"
    "</div>",
    unsafe_allow_html=True
)
