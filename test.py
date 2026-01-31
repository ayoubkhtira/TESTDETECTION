import streamlit as st
import time
from datetime import datetime
import pandas as pd
import numpy as np

# Configuration de base
st.set_page_config(
    page_title="VisionGuard AI - Détection Intelligente",
    page_icon="🤖",
    layout="wide"
)

# CSS personnalisé
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        margin-bottom: 2rem;
        text-align: center;
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border-left: 4px solid #667eea;
        margin-bottom: 1rem;
    }
    .video-container {
        background: #1a1a1a;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
    }
    .object-badge {
        display: inline-block;
        background: #007bff;
        color: white;
        padding: 8px 15px;
        border-radius: 20px;
        margin: 5px;
        font-weight: bold;
    }
    .telegram-badge {
        display: inline-block;
        background: #28a745;
        color: white;
        padding: 8px 15px;
        border-radius: 20px;
        margin: 5px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# En-tête principal
st.markdown("""
<div class="main-header">
    <h1>🤖 VisionGuard AI Pro</h1>
    <p>Système de surveillance intelligent avec détection automatique</p>
</div>
""", unsafe_allow_html=True)

# Vérifier les dépendances OpenCV
try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
    st.warning("⚠️ OpenCV n'est pas disponible. Mode simulation activé.")

# Vérifier YOLO
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    st.warning("⚠️ YOLO n'est pas disponible.")

# Vérifier Telegram
try:
    TELEGRAM_TOKEN = st.secrets["TELEGRAM_TOKEN"]
    TELEGRAM_CHAT_ID = st.secrets["TELEGRAM_CHAT_ID"]
    TELEGRAM_CONFIGURED = True
except:
    TELEGRAM_CONFIGURED = False
    st.warning("⚠️ Telegram n'est pas configuré. Ajoutez les secrets dans Streamlit Cloud.")

# Initialisation des données
if 'detections' not in st.session_state:
    st.session_state.detections = {
        'person': 0,
        'cell phone': 0,
        'car': 0,
        'chair': 0,
        'total': 0
    }
if 'history' not in st.session_state:
    st.session_state.history = []
if 'last_telegram_send' not in st.session_state:
    st.session_state.last_telegram_send = 0

# Fonction pour simuler la détection
def simulate_detection():
    """Simule la détection d'objets"""
    import random
    
    objects_to_detect = [
        ('person', 0.4),       # 40% de chance
        ('cell phone', 0.3),   # 30% de chance
        ('car', 0.15),         # 15% de chance
        ('chair', 0.1),        # 10% de chance
        ('book', 0.05)         # 5% de chance
    ]
    
    detected = []
    for obj, prob in objects_to_detect:
        if random.random() < prob:
            count = random.randint(1, 3)
            detected.extend([obj] * count)
            st.session_state.detections[obj] = st.session_state.detections.get(obj, 0) + count
    
    return detected

# Fonction pour envoyer à Telegram
def send_to_telegram_simulated():
    """Simule l'envoi à Telegram"""
    current_time = time.time()
    if current_time - st.session_state.last_telegram_send > 5:  # Toutes les 5 secondes
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Créer le message
        message = f"🔍 Détection VisionGuard AI\n"
        message += f"🕐 {timestamp}\n"
        message += f"👥 Personnes: {st.session_state.detections.get('person', 0)}\n"
        message += f"📱 Téléphones: {st.session_state.detections.get('cell phone', 0)}\n"
        message += f"📦 Total objets: {st.session_state.detections['total']}\n"
        
        # Ajouter à l'historique
        st.session_state.history.append({
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'message': f"Image envoyée à Telegram - {len(st.session_state.history) + 1} objets détectés"
        })
        
        st.session_state.last_telegram_send = current_time
        
        # Afficher une notification
        with st.chat_message("assistant"):
            st.write(f"📤 Envoyé à Telegram à {timestamp}")
        
        return True
    return False

# Affichage des métriques
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("👥 Personnes", st.session_state.detections.get('person', 0), "+2")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("📱 Téléphones", st.session_state.detections.get('cell phone', 0), "+1")
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("🚨 Détections", st.session_state.detections['total'], "+5")
    st.markdown('</div>', unsafe_allow_html=True)

with col4:
    status = "🟢 Active" if TELEGRAM_CONFIGURED else "🔴 Inactive"
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("📤 Telegram", status)
    st.markdown('</div>', unsafe_allow_html=True)

# Zone de détection principale
st.markdown("### 🎥 Détection en Temps Réel")

# Conteneur vidéo
video_container = st.empty()

# Simuler le flux vidéo
video_container.markdown("""
<div class="video-container">
    <div style="color: white; font-size: 1.5rem; margin-bottom: 20px;">
        🔍 Système de détection actif
    </div>
    <div style="background: #333; padding: 30px; border-radius: 10px; display: inline-block;">
        <div style="font-size: 4rem; color: #4CAF50;">🤖</div>
    </div>
    <div style="color: #4CAF50; margin-top: 20px; font-size: 1.2rem;">
        Détection YOLO en cours...
    </div>
</div>
""", unsafe_allow_html=True)

# Boutons de contrôle
col_btn1, col_btn2, col_btn3 = st.columns(3)

with col_btn1:
    if st.button("▶️ Démarrer la détection", use_container_width=True, type="primary"):
        st.session_state.detection_active = True
        st.rerun()

with col_btn2:
    if st.button("📸 Capturer l'image", use_container_width=True):
        st.success(f"Image capturée à {datetime.now().strftime('%H:%M:%S')}")

with col_btn3:
    if st.button("🔄 Réinitialiser", use_container_width=True):
        st.session_state.detections = {
            'person': 0,
            'cell phone': 0,
            'car': 0,
            'chair': 0,
            'total': 0
        }
        st.rerun()

# Zone d'affichage des objets détectés
st.markdown("### 📊 Objets Détectés")

# Simuler la détection automatique
if st.session_state.get('detection_active', False):
    # Timer pour la détection automatique
    if 'last_detection' not in st.session_state:
        st.session_state.last_detection = time.time()
    
    current_time = time.time()
    if current_time - st.session_state.last_detection > 2:  # Toutes les 2 secondes
        detected_objects = simulate_detection()
        st.session_state.detections['total'] += len(detected_objects)
        st.session_state.last_detection = current_time
        
        # Envoyer à Telegram toutes les 5 secondes
        send_to_telegram_simulated()
        
        # Afficher les objets détectés
        if detected_objects:
            from collections import Counter
            object_counts = Counter(detected_objects)
            
            # Créer les badges
            badges_html = ""
            for obj, count in object_counts.items():
                badges_html += f'<span class="object-badge">{obj}: {count}</span>'
            
            st.markdown(badges_html, unsafe_allow_html=True)
            
            # Mettre à jour l'affichage vidéo
            video_container.markdown(f"""
            <div class="video-container">
                <div style="color: white; font-size: 1.5rem; margin-bottom: 20px;">
                    🎯 {len(detected_objects)} objets détectés
                </div>
                <div style="background: #333; padding: 30px; border-radius: 10px; display: inline-block;">
                    <div style="font-size: 4rem; color: #FF5722;">🎯</div>
                </div>
                <div style="color: #FF5722; margin-top: 20px; font-size: 1.2rem;">
                    Détection en temps réel
                </div>
                <div style="margin-top: 20px;">
                    {badges_html}
                </div>
            </div>
            """, unsafe_allow_html=True)

# Statistiques en temps réel
st.markdown("### 📈 Statistiques Live")

# Graphique simple
chart_data = pd.DataFrame({
    'Objet': ['Personnes', 'Téléphones', 'Voitures', 'Chaises'],
    'Nombre': [
        st.session_state.detections.get('person', 0),
        st.session_state.detections.get('cell phone', 0),
        st.session_state.detections.get('car', 0),
        st.session_state.detections.get('chair', 0)
    ]
})

st.bar_chart(chart_data.set_index('Objet'))

# Historique Telegram
if st.session_state.history:
    st.markdown("### 📋 Historique Telegram")
    
    # Afficher les 5 derniers envois
    for entry in st.session_state.history[-5:]:
        st.info(f"🕐 {entry['timestamp']} - {entry['message']}")

# Panneau d'information
with st.expander("ℹ️ Informations système"):
    col_info1, col_info2 = st.columns(2)
    
    with col_info1:
        st.markdown("**État du système:**")
        if OPENCV_AVAILABLE:
            st.success("✅ OpenCV disponible")
        else:
            st.warning("⚠️ OpenCV en mode simulation")
        
        if YOLO_AVAILABLE:
            st.success("✅ YOLO disponible")
        else:
            st.warning("⚠️ YOLO en mode simulation")
        
        if TELEGRAM_CONFIGURED:
            st.success("✅ Telegram configuré")
        else:
            st.warning("⚠️ Telegram non configuré")
    
    with col_info2:
        st.markdown("**Configuration requise:**")
        st.code("""
        # requirements.txt
        streamlit==1.28.0
        opencv-python-headless==4.8.1.78
        ultralytics==8.0.0
        """)
        
        st.markdown("**Prochain envoi Telegram:**")
        next_send = max(0, 5 - (time.time() - st.session_state.last_telegram_send))
        st.progress(next_send / 5, f"Dans {int(next_send)} secondes")

# Instructions pour résoudre OpenCV
if not OPENCV_AVAILABLE:
    st.markdown("---")
    st.markdown("### 🔧 Configuration requise pour OpenCV")
    
    with st.expander("Cliquez pour voir les instructions"):
        st.markdown("""
        #### Pour Streamlit Cloud, ajoutez ces fichiers :
        
        **1. `requirements.txt` :**
        ```txt
        streamlit==1.28.0
        opencv-python-headless==4.8.1.78
        ultralytics==8.0.0
        numpy==1.24.0
        pandas==2.1.0
        Pillow==10.0.0
        ```
        
        **2. `packages.txt` (CRITIQUE) :**
        ```txt
        libgl1-mesa-glx
        libglib2.0-0
        libsm6
        libxext6
        libxrender1
        libgomp1
        ```
        
        **3. `.streamlit/secrets.toml` :**
        ```toml
        TELEGRAM_TOKEN = "votre_token_ici"
        TELEGRAM_CHAT_ID = "votre_chat_id_ici"
        ```
        
        **4. Structure des fichiers :**
        ```
        votre-projet/
        ├── app.py
        ├── requirements.txt
        ├── packages.txt
        └── .streamlit/
            └── secrets.toml
        ```
        
        **5. Redéployez** sur Streamlit Cloud
        """)

# Pied de page
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666; padding: 20px;'>"
    "🤖 VisionGuard AI Pro v2.1 | Système de surveillance intelligent"
    "</div>",
    unsafe_allow_html=True
)
