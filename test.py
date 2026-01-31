import streamlit as st
import sys
import os
import time
from datetime import datetime

# --- GESTION DES IMPORTATIONS AVEC FALLBACK ---
try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError as e:
    OPENCV_AVAILABLE = False
    st.warning(f"⚠️ OpenCV n'est pas disponible: {e}")
    st.info("Utilisation du mode simulation...")

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    st.warning("⚠️ Module 'requests' non disponible")

try:
    import pandas as pd
    import numpy as np
    PANDAS_NUMPY_AVAILABLE = True
except ImportError:
    PANDAS_NUMPY_AVAILABLE = False
    st.warning("⚠️ Modules 'pandas' ou 'numpy' non disponibles")

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    st.warning("⚠️ Module 'ultralytics' non disponible")

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    st.warning("⚠️ Module 'PIL' non disponible")

try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    st.warning("⚠️ Module 'plotly' non disponible")

# --- CONFIGURATION DE BASE ---
st.set_page_config(
    page_title="VisionGuard AI Pro",
    layout="wide",
    page_icon="🤖",
    initial_sidebar_state="expanded"
)

# --- SECRETS TELEGRAM ---
TELEGRAM_CONFIGURED = False
if not OPENCV_AVAILABLE or not REQUESTS_AVAILABLE:
    st.warning("⚠️ Fonctionnalité Telegram désactivée (dépendances manquantes)")
else:
    try:
        TELEGRAM_TOKEN = st.secrets.get("TELEGRAM_TOKEN", "")
        TELEGRAM_CHAT_ID = st.secrets.get("TELEGRAM_CHAT_ID", "")
        TELEGRAM_CONFIGURED = bool(TELEGRAM_TOKEN and TELEGRAM_CHAT_ID)
    except:
        TELEGRAM_CONFIGURED = False
        st.sidebar.info("ℹ️ Configurez Telegram dans secrets.toml")

# --- CSS AVEC FONT AWESOME ---
st.markdown("""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border-left: 4px solid #667eea;
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.12);
    }
    
    .metric-icon {
        font-size: 2rem;
        margin-bottom: 0.5rem;
        color: #667eea;
    }
    
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
    }
    
    .status-badge {
        display: inline-flex;
        align-items: center;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        margin: 0.25rem;
        font-weight: 600;
    }
    
    .status-success {
        background: linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%);
        color: white;
    }
    
    .status-warning {
        background: linear-gradient(135deg, #FF9800 0%, #F57C00 100%);
        color: white;
    }
    
    .status-error {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
        color: white;
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #2c3e50 0%, #1a1a2e 100%);
        color: white;
    }
    
    .tab-icon {
        margin-right: 8px;
    }
    
    .demo-container {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# --- INITIALISATION DE SESSION ---
if 'history' not in st.session_state:
    st.session_state.history = []
if 'detection_stats' not in st.session_state:
    st.session_state.detection_stats = {}
if 'is_running' not in st.session_state:
    st.session_state.is_running = False
if 'last_capture' not in st.session_state:
    st.session_state.last_capture = None

# --- FONCTIONS ---
def send_telegram_alert(image_np=None, caption="Alerte VisionGuard"):
    """Envoie une alerte Telegram"""
    if not TELEGRAM_CONFIGURED or not REQUESTS_AVAILABLE:
        return False
    
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': caption,
            'parse_mode': 'Markdown'
        }
        response = requests.post(url, data=data, timeout=10)
        return response.status_code == 200
    except Exception as e:
        st.sidebar.error(f"Erreur Telegram: {str(e)}")
        return False

def simulate_detection():
    """Simule la détection d'objets pour la démo"""
    import random
    objects = ['person', 'cell phone', 'car', 'chair', 'book', 'laptop', 'bottle']
    weights = [0.3, 0.2, 0.1, 0.15, 0.1, 0.1, 0.05]
    
    detected = {}
    for _ in range(random.randint(1, 5)):
        obj = random.choices(objects, weights=weights)[0]
        detected[obj] = detected.get(obj, 0) + 1
    
    return detected

# --- UI : BARRE LATERALE ---
with st.sidebar:
    st.markdown("""
        <div style="text-align: center; padding: 1rem 0;">
            <i class="fas fa-robot" style="font-size: 2.5rem; color: white; margin-bottom: 0.5rem;"></i>
            <h2 style="color: white; margin-bottom: 0.5rem;">VisionGuard AI</h2>
            <p style="color: #b3b3b3; font-size: 0.9rem;">Système de surveillance intelligent</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Statut des dépendances
    with st.expander("<i class='fas fa-info-circle'></i> Statut du système", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            status_color = "🟢" if OPENCV_AVAILABLE else "🔴"
            st.metric("OpenCV", status_color)
        with col2:
            status_color = "🟢" if YOLO_AVAILABLE else "🔴"
            st.metric("YOLO", status_color)
        
        if not OPENCV_AVAILABLE:
            st.error("""
            **OpenCV non disponible**
            - Ajoutez `opencv-python-headless` à requirements.txt
            - Ajoutez `libgl1-mesa-glx` à packages.txt
            """)
    
    st.divider()
    
    # Configuration Telegram
    with st.expander("<i class='fas fa-paper-plane'></i> Configuration Telegram"):
        if TELEGRAM_CONFIGURED:
            st.success("<i class='fas fa-check-circle'></i> Telegram configuré")
            st.caption(f"Chat ID: {TELEGRAM_CHAT_ID[:8]}...")
        else:
            st.warning("<i class='fas fa-exclamation-triangle'></i> Telegram non configuré")
            st.info("Ajoutez TELEGRAM_TOKEN et TELEGRAM_CHAT_ID dans secrets.toml")
    
    st.divider()
    
    # Paramètres
    with st.expander("<i class='fas fa-cog'></i> Paramètres"):
        conf_level = st.slider("Seuil de confiance", 0.1, 0.9, 0.6, 0.05,
                              disabled=not YOLO_AVAILABLE)
        cooldown = st.slider("Délai entre alertes (s)", 5, 300, 30, 5)
        alert_mode = st.selectbox("Mode d'alerte", 
                                 ["Téléphone détecté", 
                                  "Personne + Téléphone", 
                                  "Tout objet suspect"],
                                 index=1)
    
    st.divider()
    
    # Contrôles
    col1, col2 = st.columns(2)
    with col1:
        if st.button("<i class='fas fa-play'></i> Démarrer", 
                    use_container_width=True, 
                    type="primary",
                    disabled=not OPENCV_AVAILABLE and not YOLO_AVAILABLE):
            st.session_state.is_running = True
            st.rerun()
    
    with col2:
        if st.button("<i class='fas fa-stop'></i> Arrêter", 
                    use_container_width=True):
            st.session_state.is_running = False
            st.rerun()
    
    st.divider()
    
    # Statistiques
    if st.session_state.detection_stats:
        st.markdown("<i class='fas fa-chart-bar'></i> **Statistiques**")
        for obj, count in list(st.session_state.detection_stats.items())[:5]:
            st.progress(min(count/20, 1.0), f"{obj}: {count}")

# --- UI : EN-TÊTE PRINCIPALE ---
st.markdown("""
    <div class="main-header">
        <div style="display: flex; align-items: center; gap: 20px;">
            <i class="fas fa-robot" style="font-size: 3rem;"></i>
            <div>
                <h1 style="margin: 0; font-size: 2.5rem;">VisionGuard AI Pro</h1>
                <p style="margin: 0.5rem 0 0 0; font-size: 1.1rem; opacity: 0.9;">
                    <i class="fas fa-shield-alt"></i> Système avancé de surveillance et d'analyse
                </p>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- UI : MÉTRIQUES ---
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown('<div class="metric-icon"><i class="fas fa-users"></i></div>', unsafe_allow_html=True)
    person_count = st.session_state.detection_stats.get('person', 0)
    st.metric("Personnes", person_count, delta=None)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown('<div class="metric-icon"><i class="fas fa-mobile-alt"></i></div>', unsafe_allow_html=True)
    phone_count = st.session_state.detection_stats.get('cell phone', 0)
    st.metric("Téléphones", phone_count, delta=None)
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown('<div class="metric-icon"><i class="fas fa-bell"></i></div>', unsafe_allow_html=True)
    alert_count = len([h for h in st.session_state.history if "Alerte" in h.get("Statut", "")])
    st.metric("Alertes", alert_count, delta=None)
    st.markdown('</div>', unsafe_allow_html=True)

with col4:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown('<div class="metric-icon"><i class="fas fa-database"></i></div>', unsafe_allow_html=True)
    total_detections = sum(st.session_state.detection_stats.values())
    st.metric("Détections", total_detections, delta=None)
    st.markdown('</div>', unsafe_allow_html=True)

# --- UI : ONGLETS ---
tab1, tab2, tab3 = st.tabs([
    "<i class='fas fa-video'></i> Surveillance",
    "<i class='fas fa-chart-line'></i> Analytics",
    "<i class='fas fa-history'></i> Historique"
])

with tab1:
    if not OPENCV_AVAILABLE:
        # Mode simulation
        st.warning("""
        <div style="text-align: center; padding: 2rem;">
            <i class="fas fa-exclamation-triangle" style="font-size: 3rem; color: #FF9800; margin-bottom: 1rem;"></i>
            <h3>Mode Simulation Activé</h3>
            <p>OpenCV n'est pas disponible. L'application fonctionne en mode simulation.</p>
        </div>
        """, unsafe_allow_html=True)
        
        col_video, col_stats = st.columns([2, 1])
        
        with col_video:
            st.markdown("### <i class='fas fa-video'></i> Simulation vidéo")
            
            # Image de démonstration
            demo_img = """
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                       padding: 4px; border-radius: 12px; margin: 1rem 0;">
                <div style="background: #1a1a1a; border-radius: 8px; padding: 2rem; text-align: center;">
                    <i class="fas fa-camera" style="font-size: 4rem; color: #667eea; margin: 1rem 0;"></i>
                    <p style="color: #aaa; margin: 1rem 0;">Flux vidéo simulé</p>
                    <div style="display: flex; justify-content: center; gap: 20px; margin: 2rem 0;">
                        <div style="background: rgba(0,255,0,0.2); padding: 10px; border-radius: 5px;">
                            <i class="fas fa-user"></i> Personne
                        </div>
                        <div style="background: rgba(255,0,0,0.2); padding: 10px; border-radius: 5px;">
                            <i class="fas fa-mobile-alt"></i> Téléphone
                        </div>
                    </div>
                </div>
            </div>
            """
            st.markdown(demo_img, unsafe_allow_html=True)
            
            # Contrôles simulation
            col_controls = st.columns(3)
            with col_controls[0]:
                if st.button("<i class='fas fa-bolt'></i> Simuler détection", use_container_width=True):
                    detected = simulate_detection()
                    for obj, count in detected.items():
                        st.session_state.detection_stats[obj] = st.session_state.detection_stats.get(obj, 0) + count
                    
                    # Vérifier alerte
                    if detected.get('cell phone', 0) > 0:
                        timestamp = datetime.now().strftime("%H:%M:%S")
                        history_entry = {
                            "Heure": timestamp,
                            "Téléphones": detected.get('cell phone', 0),
                            "Personnes": detected.get('person', 0),
                            "Objets": detected,
                            "Statut": "Alerte simulée"
                        }
                        st.session_state.history.insert(0, history_entry)
                        st.toast(f"📱 {detected.get('cell phone', 0)} téléphone(s) détecté(s) à {timestamp}")
            
            with col_controls[1]:
                if st.button("<i class='fas fa-redo'></i> Réinitialiser", use_container_width=True):
                    st.session_state.detection_stats = {}
                    st.rerun()
            
            with col_controls[2]:
                if st.button("<i class='fas fa-camera'></i> Capture", use_container_width=True):
                    st.session_state.last_capture = datetime.now()
                    st.toast("<i class='fas fa-check'></i> Capture simulée", icon="✅")
        
        with col_stats:
            st.markdown("### <i class='fas fa-bullseye'></i> Détections simulées")
            
            if st.session_state.detection_stats:
                for obj, count in sorted(st.session_state.detection_stats.items()):
                    icon = "👤" if obj == "person" else "📱" if "phone" in obj else "📦"
                    st.markdown(f"**{icon} {obj.capitalize()}**: {count}")
            else:
                st.info("Aucune détection simulée")
                
            st.markdown("---")
            st.markdown("### <i class='fas fa-info-circle'></i> Instructions")
            st.info("""
            Pour activer la vraie détection :
            1. Ajoutez `opencv-python-headless` à requirements.txt
            2. Ajoutez `libgl1-mesa-glx` à packages.txt
            3. Redéployez l'application
            """)
    
    elif st.session_state.is_running and OPENCV_AVAILABLE and YOLO_AVAILABLE:
        # Mode réel avec OpenCV
        try:
            cap = cv2.VideoCapture(0)
            if cap.isOpened():
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                
                video_placeholder = st.empty()
                stop_button = st.button("<i class='fas fa-stop-circle'></i> Arrêter la surveillance", 
                                       use_container_width=True)
                
                model = YOLO("yolov8n.pt")
                last_alert_time = 0
                
                while cap.isOpened() and st.session_state.is_running and not stop_button:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    
                    # Détection
                    results = model(frame, conf=conf_level)
                    
                    # Analyse des résultats
                    names = model.names
                    detected_objects = {}
                    if results and len(results) > 0:
                        boxes = results[0].boxes
                        if boxes is not None:
                            for c in boxes.cls:
                                obj_name = names[int(c)]
                                detected_objects[obj_name] = detected_objects.get(obj_name, 0) + 1
                    
                    # Mise à jour stats
                    for obj, count in detected_objects.items():
                        st.session_state.detection_stats[obj] = st.session_state.detection_stats.get(obj, 0) + count
                    
                    # Logique d'alerte
                    current_time = time.time()
                    phone_count = detected_objects.get('cell phone', 0)
                    
                    if phone_count > 0 and (current_time - last_alert_time > cooldown):
                        timestamp = datetime.now().strftime("%H:%M:%S")
                        
                        # Envoyer alerte Telegram
                        if TELEGRAM_CONFIGURED:
                            alert_msg = f"""🚨 ALERTE VisionGuard
Heure: {timestamp}
Téléphones détectés: {phone_count}
Personnes détectées: {detected_objects.get('person', 0)}"""
                            send_telegram_alert(caption=alert_msg)
                        
                        # Sauvegarder historique
                        history_entry = {
                            "Heure": timestamp,
                            "Téléphones": phone_count,
                            "Personnes": detected_objects.get('person', 0),
                            "Objets": detected_objects,
                            "Statut": "Alerte envoyée" if TELEGRAM_CONFIGURED else "Alerte détectée"
                        }
                        st.session_state.history.insert(0, history_entry)
                        last_alert_time = current_time
                        
                        st.toast(f"🚨 {phone_count} téléphone(s) détecté(s)")
                    
                    # Afficher le flux
                    if results and len(results) > 0:
                        annotated_frame = results[0].plot()
                        video_placeholder.image(annotated_frame, channels="BGR", 
                                              use_column_width=True)
                    
                    if stop_button:
                        st.session_state.is_running = False
                        break
                
                cap.release()
                cv2.destroyAllWindows()
            else:
                st.error("Impossible d'accéder à la caméra")
        except Exception as e:
            st.error(f"Erreur OpenCV: {str(e)}")
            st.info("Revenez au mode simulation")
    else:
        # Écran d'attente
        st.markdown("""
            <div class="demo-container">
                <i class="fas fa-play-circle" style="font-size: 4rem; color: #667eea; margin-bottom: 1rem;"></i>
                <h3>Prêt à démarrer</h3>
                <p>Cliquez sur "Démarrer" dans la barre latérale pour lancer la surveillance</p>
            </div>
        """, unsafe_allow_html=True)

with tab2:
    st.markdown("### <i class='fas fa-chart-bar'></i> Analytics")
    
    if st.session_state.history and PANDAS_NUMPY_AVAILABLE and PLOTLY_AVAILABLE:
        try:
            # Préparation des données
            df = pd.DataFrame(st.session_state.history)
            
            if not df.empty:
                # Graphique 1: Évolution des détections
                fig1 = px.line(df, x='Heure', y='Personnes', 
                              title="Personnes détectées par heure")
                st.plotly_chart(fig1, use_container_width=True)
                
                # Graphique 2: Répartition des objets
                all_objects = []
                for obj_dict in df['Objets']:
                    if isinstance(obj_dict, dict):
                        for obj, count in obj_dict.items():
                            all_objects.extend([obj] * count)
                
                if all_objects:
                    obj_counts = pd.Series(all_objects).value_counts().head(10)
                    fig2 = px.bar(x=obj_counts.index, y=obj_counts.values,
                                 title="Top 10 des objets détectés")
                    st.plotly_chart(fig2, use_container_width=True)
        except Exception as e:
            st.error(f"Erreur d'analyse: {str(e)}")
    else:
        st.info("""
        <div style="text-align: center; padding: 3rem;">
            <i class="fas fa-chart-line" style="font-size: 3rem; color: #667eea; margin-bottom: 1rem;"></i>
            <h4>Aucune donnée d'analyse disponible</h4>
            <p>Lancez la surveillance pour générer des données d'analyse</p>
        </div>
        """, unsafe_allow_html=True)

with tab3:
    st.markdown("### <i class='fas fa-list'></i> Historique des événements")
    
    if st.session_state.history and PANDAS_NUMPY_AVAILABLE:
        try:
            df_display = pd.DataFrame(st.session_state.history)
            
            # Formater les colonnes
            if 'Objets' in df_display.columns:
                def format_objects(obj):
                    if isinstance(obj, dict):
                        return ', '.join([f"{k}: {v}" for k, v in obj.items()])
                    return str(obj)
                df_display['Objets'] = df_display['Objets'].apply(format_objects)
            
            # Afficher le tableau
            st.dataframe(df_display, use_container_width=True, height=300)
            
            # Boutons d'export
            col1, col2 = st.columns(2)
            with col1:
                if st.button("<i class='fas fa-download'></i> Exporter CSV", use_container_width=True):
                    csv = df_display.to_csv(index=False)
                    st.download_button(
                        "Télécharger",
                        csv,
                        "historique.csv",
                        "text/csv",
                        use_container_width=True
                    )
            with col2:
                if st.button("<i class='fas fa-trash'></i> Effacer historique", use_container_width=True):
                    st.session_state.history = []
                    st.rerun()
        except Exception as e:
            st.error(f"Erreur d'affichage: {str(e)}")
    else:
        st.info("""
        <div style="text-align: center; padding: 3rem;">
            <i class="fas fa-history" style="font-size: 3rem; color: #667eea; margin-bottom: 1rem;"></i>
            <h4>Aucun historique disponible</h4>
            <p>Les événements s'afficheront ici après détection</p>
        </div>
        """, unsafe_allow_html=True)

# --- PIED DE PAGE ---
st.markdown("""
    <div style="text-align: center; margin-top: 3rem; padding: 1.5rem; color: #666; 
                border-top: 1px solid #eee; background: rgba(255,255,255,0.5); border-radius: 10px;">
        <div style="display: flex; justify-content: center; align-items: center; gap: 10px; margin-bottom: 0.5rem;">
            <i class="fas fa-robot" style="color: #667eea;"></i>
            <h4 style="margin: 0;">VisionGuard AI Pro</h4>
        </div>
        <p style="margin: 0; font-size: 0.9rem;">
            Système de surveillance intelligent • v2.0
        </p>
        <p style="margin: 0.5rem 0 0 0; font-size: 0.8rem; opacity: 0.7;">
            Compatible Streamlit Cloud • Mode simulation activé
        </p>
    </div>
""", unsafe_allow_html=True)

# --- CONFIGURATION REQUISE ---
if not OPENCV_AVAILABLE:
    with st.expander("⚠️ Configuration requise pour Streamlit Cloud"):
        st.markdown("""
        ### Pour activer la vraie détection vidéo :
        
        **1. Fichier `requirements.txt` :**
        ```txt
        streamlit==1.28.0
        opencv-python-headless==4.8.1.78
        requests==2.31.0
        pandas==2.1.0
        numpy==1.24.0
        ultralytics==8.0.0
        Pillow==10.0.0
        plotly==5.17.0
        ```
        
        **2. Fichier `packages.txt` :**
        ```txt
        libgl1-mesa-glx
        libglib2.0-0
        libsm6
        libxext6
        libxrender1
        libgomp1
        ```
        
        **3. Structure du projet :**
        ```
        your-repo/
        ├── app.py              # Ce fichier
        ├── requirements.txt    # Dépendances Python
        ├── packages.txt       # Dépendances système
        └── .streamlit/
            └── secrets.toml   # Configuration Telegram
        ```
        
        **4. Redéployez** sur Streamlit Cloud
        """)
