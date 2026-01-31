import streamlit as st
import cv2
import requests
import time
import os
import pandas as pd
import numpy as np
from datetime import datetime
from ultralytics import YOLO
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
import warnings
warnings.filterwarnings('ignore')

# --- CONFIGURATION ---
st.set_page_config(
    page_title="VisionGuard AI Pro",
    layout="wide",
    page_icon="🤖",
    initial_sidebar_state="expanded"
)

# --- SECRETS TELEGRAM ---
try:
    TELEGRAM_TOKEN = st.secrets["TELEGRAM_TOKEN"]
    TELEGRAM_CHAT_ID = st.secrets["TELEGRAM_CHAT_ID"]
    TELEGRAM_CONFIGURED = True
except (KeyError, FileNotFoundError):
    TELEGRAM_TOKEN = None
    TELEGRAM_CHAT_ID = None
    TELEGRAM_CONFIGURED = False

# --- CSS POUR THÈME MODERNE AVEC FONT AWESOME ---
st.markdown("""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Poppins:wght@400;500;600;700&display=swap">
    
    <style>
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2.5rem;
        border-radius: 20px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 12px 40px rgba(0,0,0,0.15);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 1px, transparent 1px);
        background-size: 50px 50px;
        opacity: 0.1;
        z-index: 0;
    }
    
    .main-header-content {
        position: relative;
        z-index: 1;
    }
    
    .stApp {
        background: linear-gradient(135deg, #f8f9ff 0%, #eef1f9 100%);
    }
    
    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9ff 100%);
        padding: 1.8rem;
        border-radius: 16px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.08);
        border: 1px solid rgba(255,255,255,0.3);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: linear-gradient(to bottom, #667eea, #764ba2);
    }
    
    .metric-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 15px 35px rgba(102, 126, 234, 0.15);
    }
    
    .metric-icon {
        font-size: 2.2rem;
        margin-bottom: 0.8rem;
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.85rem 1.8rem;
        border-radius: 12px;
        font-weight: 600;
        transition: all 0.3s ease;
        font-family: 'Poppins', sans-serif;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.25);
    }
    
    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }
    
    .alert-badge {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
        color: white;
        padding: 0.5rem 1.2rem;
        border-radius: 25px;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 8px;
        box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3);
    }
    
    .stat-card {
        background: white;
        padding: 1.2rem;
        border-radius: 12px;
        margin: 0.5rem 0;
        box-shadow: 0 3px 15px rgba(0,0,0,0.05);
        border-left: 3px solid #667eea;
        transition: transform 0.2s ease;
    }
    
    .stat-card:hover {
        transform: translateX(5px);
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
        color: white;
    }
    
    .telegram-status {
        padding: 0.8rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        text-align: center;
        font-weight: 600;
        border: 2px solid transparent;
    }
    
    .telegram-success {
        background: linear-gradient(135deg, rgba(76, 175, 80, 0.15) 0%, rgba(46, 125, 50, 0.15) 100%);
        border-color: #4CAF50;
        color: #4CAF50;
    }
    
    .telegram-warning {
        background: linear-gradient(135deg, rgba(255, 152, 0, 0.15) 0%, rgba(239, 108, 0, 0.15) 100%);
        border-color: #FF9800;
        color: #FF9800;
    }
    
    .tab-icon {
        margin-right: 10px;
        font-size: 1.2em;
    }
    
    .icon-large {
        font-size: 2.5rem;
        margin-bottom: 1rem;
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .feature-icon {
        font-size: 2rem;
        margin-bottom: 0.5rem;
        color: #667eea;
    }
    
    .pulse-animation {
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    .glass-effect {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .gradient-text {
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 700;
    }
    </style>
""", unsafe_allow_html=True)

# --- INITIALISATION ---
if 'history' not in st.session_state:
    st.session_state.history = []
if 'detection_stats' not in st.session_state:
    st.session_state.detection_stats = Counter()
if 'last_analysis_time' not in st.session_state:
    st.session_state.last_analysis_time = 0
if 'is_running' not in st.session_state:
    st.session_state.is_running = False

@st.cache_resource
def load_model():
    """Charge le modèle YOLO"""
    return YOLO("yolov8n.pt")

model = load_model()

# --- FONCTION D'ENVOI TELEGRAM ---
def send_telegram_alert(image_np, caption):
    """Envoie une alerte Telegram"""
    if not TELEGRAM_CONFIGURED:
        return False
    
    try:
        temp_path = "temp_alert.jpg"
        cv2.imwrite(temp_path, cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR))
        
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
        with open(temp_path, 'rb') as photo:
            response = requests.post(
                url, 
                data={'chat_id': TELEGRAM_CHAT_ID, 'caption': caption, 'parse_mode': 'Markdown'},
                files={'photo': photo},
                timeout=10
            )
        
        if os.path.exists(temp_path):
            os.remove(temp_path)
            
        return response.status_code == 200
        
    except Exception as e:
        st.sidebar.error(f"Erreur Telegram: {str(e)}")
        return False

# --- UI : BARRE LATERALE ---
with st.sidebar:
    st.markdown("""
        <div style="text-align: center; padding: 1.5rem 0;">
            <div class="icon-large">
                <i class="fas fa-robot"></i>
            </div>
            <h2 style="color: white; margin-bottom: 0.5rem; font-family: 'Poppins', sans-serif;">VisionGuard AI</h2>
            <p style="color: #b3b3b3; font-size: 0.9rem;">Système de surveillance intelligent</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Statut Telegram
    with st.expander("<i class='fas fa-paper-plane'></i> Configuration Telegram", expanded=True):
        if TELEGRAM_CONFIGURED:
            st.markdown('<div class="telegram-status telegram-success">'
                       '<i class="fas fa-check-circle"></i> Telegram configuré</div>', 
                       unsafe_allow_html=True)
            st.caption(f"Chat ID: {TELEGRAM_CHAT_ID[:4]}...{TELEGRAM_CHAT_ID[-4:]}")
        else:
            st.markdown('<div class="telegram-status telegram-warning">'
                       '<i class="fas fa-exclamation-triangle"></i> Telegram non configuré</div>', 
                       unsafe_allow_html=True)
            st.caption("Ajoutez TELEGRAM_TOKEN et TELEGRAM_CHAT_ID dans les secrets Streamlit")
    
    st.divider()
    
    with st.expander("<i class='fas fa-sliders-h'></i> Paramètres de détection", expanded=True):
        conf_level = st.slider("Seuil de confiance", 0.1, 0.9, 0.6, 0.05,
                              help="Niveau de confiance minimum pour les détections")
        cooldown = st.slider("Délai entre alertes (s)", 5, 300, 30, 5,
                            help="Temps minimum entre deux alertes consécutives")
        require_person = st.toggle("Alerte uniquement avec personne", value=True,
                                  help="N'envoie des alertes que si une personne est détectée")
        enable_audio = st.toggle("Notifications sonores", value=False,
                                help="Active les alertes sonores locales")
    
    st.divider()
    
    # Contrôles
    col1, col2 = st.columns(2)
    with col1:
        if st.button("<i class='fas fa-play'></i> Démarrer", use_container_width=True, 
                    type="primary", disabled=not TELEGRAM_CONFIGURED):
            st.session_state.is_running = True
            st.rerun()
    
    with col2:
        if st.button("<i class='fas fa-stop'></i> Arrêter", use_container_width=True):
            st.session_state.is_running = False
            st.rerun()
    
    st.divider()
    
    # Statistiques en temps réel
    if st.session_state.detection_stats:
        st.markdown("### <i class='fas fa-chart-bar'></i> Statistiques actuelles")
        for obj, count in st.session_state.detection_stats.most_common(5):
            col_prog, col_text = st.columns([3, 1])
            with col_prog:
                st.progress(min(count/10, 1.0))
            with col_text:
                st.caption(f"{obj}: {count}")

# --- UI : EN-TÊTE PRINCIPALE ---
st.markdown("""
    <div class="main-header">
        <div class="main-header-content">
            <div style="display: flex; align-items: center; gap: 20px; margin-bottom: 1rem;">
                <div class="pulse-animation">
                    <i class="fas fa-robot" style="font-size: 3.5rem;"></i>
                </div>
                <div>
                    <h1 style="margin: 0; font-size: 2.8rem; font-family: 'Poppins', sans-serif;">
                        VisionGuard <span class="gradient-text">AI Pro</span>
                    </h1>
                    <p style="margin: 0.5rem 0 0 0; font-size: 1.2rem; opacity: 0.9;">
                        <i class="fas fa-brain"></i> Système avancé de surveillance et d'analyse en temps réel
                    </p>
                </div>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- UI : MÉTRIQUES EN TEMPS RÉEL ---
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown('<div class="metric-icon"><i class="fas fa-users"></i></div>', unsafe_allow_html=True)
    st.metric("Personnes détectées", "0", delta=None)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown('<div class="metric-icon"><i class="fas fa-mobile-alt"></i></div>', unsafe_allow_html=True)
    st.metric("Téléphones détectés", "0", delta=None)
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown('<div class="metric-icon"><i class="fas fa-bell"></i></div>', unsafe_allow_html=True)
    status = "Active" if TELEGRAM_CONFIGURED else "Inactive"
    st.metric("Notifications", status, delta=None)
    st.markdown('</div>', unsafe_allow_html=True)

with col4:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown('<div class="metric-icon"><i class="fas fa-tachometer-alt"></i></div>', unsafe_allow_html=True)
    st.metric("Performance", "0 FPS", delta=None)
    st.markdown('</div>', unsafe_allow_html=True)

# --- UI : PRINCIPAL AVEC ONGLETS STYLÉS ---
tab1, tab2, tab3 = st.tabs([
    "<i class='fas fa-video'></i> Surveillance", 
    "<i class='fas fa-chart-line'></i> Analytics", 
    "<i class='fas fa-history'></i> Historique"
])

with tab1:
    col_video, col_stats = st.columns([2, 1])
    
    with col_video:
        st.markdown("### <i class='fas fa-broadcast-tower'></i> Flux vidéo en direct")
        
        # Placeholder pour la vidéo avec cadre stylisé
        video_container = st.empty()
        video_container.markdown("""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                       padding: 4px; border-radius: 16px; margin-bottom: 20px;">
                <div style="background: #1a1a1a; border-radius: 12px; padding: 20px; text-align: center;">
                    <i class="fas fa-satellite-dish" style="font-size: 3rem; color: #667eea; margin: 20px 0;"></i>
                    <p style="color: #aaa;">En attente du flux vidéo...</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Contrôles vidéo
        col_controls = st.columns(3)
        with col_controls[0]:
            if st.button("<i class='fas fa-camera'></i> Capture", use_container_width=True):
                st.session_state.last_capture = datetime.now()
                st.toast("<i class='fas fa-check-circle'></i> Capture effectuée!", icon="✅")
        with col_controls[1]:
            record = st.toggle("<i class='fas fa-record-vinyl'></i> Enregistrer", value=False, disabled=True)
        with col_controls[2]:
            if st.button("<i class='fas fa-redo'></i> Réinitialiser", use_container_width=True):
                st.session_state.detection_stats = Counter()
                st.rerun()
    
    with col_stats:
        st.markdown("### <i class='fas fa-binoculars'></i> Détections en cours")
        stats_placeholder = st.empty()
        stats_placeholder.markdown("""
            <div style="background: white; padding: 20px; border-radius: 12px; text-align: center;">
                <i class="fas fa-search" style="font-size: 2rem; color: #667eea; margin-bottom: 10px;"></i>
                <p style="color: #666;">En attente de détections...</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### <i class='fas fa-exclamation-triangle'></i> Alertes récentes")
        alert_placeholder = st.empty()
        alert_placeholder.markdown("""
            <div style="background: white; padding: 20px; border-radius: 12px; text-align: center;">
                <i class="fas fa-bell-slash" style="font-size: 2rem; color: #aaa; margin-bottom: 10px;"></i>
                <p style="color: #666;">Aucune alerte récente</p>
            </div>
        """, unsafe_allow_html=True)

with tab2:
    st.markdown("### <i class='fas fa-chart-pie'></i> Analytics approfondis")
    
    if st.session_state.history:
        # Graphique temporel
        df_history = pd.DataFrame(st.session_state.history)
        df_history['Heure'] = pd.to_datetime(df_history['Heure'])
        
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            fig1 = px.line(df_history, x='Heure', y='Personnes', 
                          title="<b>Évolution du nombre de personnes</b>",
                          markers=True,
                          line_shape="spline",
                          color_discrete_sequence=['#667eea'])
            fig1.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_family="Inter"
            )
            st.plotly_chart(fig1, use_container_width=True)
        
        with col_chart2:
            if 'Objets' in df_history.columns:
                try:
                    all_objects = []
                    for obj_list in df_history['Objets']:
                        if isinstance(obj_list, dict):
                            for obj, count in obj_list.items():
                                all_objects.extend([obj] * count)
                    
                    if all_objects:
                        obj_counts = pd.Series(all_objects).value_counts().head(10)
                        fig2 = px.bar(x=obj_counts.index, y=obj_counts.values,
                                     title="<b>Top 10 des objets détectés</b>",
                                     color=obj_counts.values,
                                     color_continuous_scale='Viridis')
                        fig2.update_layout(
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            font_family="Inter",
                            showlegend=False
                        )
                        st.plotly_chart(fig2, use_container_width=True)
                except:
                    st.info("Données d'objets indisponibles")
    else:
        st.markdown("""
            <div style="text-align: center; padding: 4rem 2rem; background: white; border-radius: 15px;">
                <i class="fas fa-chart-line" style="font-size: 4rem; color: #667eea; margin-bottom: 1rem;"></i>
                <h3 style="color: #667eea;">Aucune donnée analytique</h3>
                <p style="color: #666;">Lancez la surveillance pour générer des données d'analyse</p>
            </div>
        """, unsafe_allow_html=True)

with tab3:
    st.markdown("### <i class='fas fa-database'></i> Historique complet")
    
    if st.session_state.history:
        df_display = pd.DataFrame(st.session_state.history)
        
        # Formater les colonnes
        if 'Objets' in df_display.columns:
            df_display['Objets'] = df_display['Objets'].apply(
                lambda x: ', '.join([f"{k}({v})" for k, v in x.items()]) if isinstance(x, dict) else str(x)
            )
        
        # Afficher le tableau avec style
        st.dataframe(
            df_display,
            use_container_width=True,
            height=400,
            column_config={
                "Heure": st.column_config.DatetimeColumn("🕒 Heure"),
                "Téléphones": st.column_config.NumberColumn("📱 Téléphones"),
                "Personnes": st.column_config.NumberColumn("👥 Personnes"),
                "Statut": st.column_config.TextColumn("📊 Statut")
            }
        )
        
        # Boutons d'export
        col_export = st.columns(3)
        with col_export[0]:
            if st.button("<i class='fas fa-file-csv'></i> Exporter CSV", use_container_width=True):
                csv = df_display.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="Télécharger CSV",
                    data=csv,
                    file_name="visionguard_historique.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        with col_export[1]:
            if st.button("<i class='fas fa-file-excel'></i> Exporter Excel", use_container_width=True):
                excel_buffer = df_display.to_excel(index=False)
                st.download_button(
                    label="Télécharger Excel",
                    data=excel_buffer,
                    file_name="visionguard_historique.xlsx",
                    mime="application/vnd.ms-excel",
                    use_container_width=True
                )
        with col_export[2]:
            if st.button("<i class='fas fa-trash-alt'></i> Effacer", use_container_width=True):
                st.session_state.history = []
                st.rerun()
    else:
        st.markdown("""
            <div style="text-align: center; padding: 4rem 2rem; background: white; border-radius: 15px;">
                <i class="fas fa-history" style="font-size: 4rem; color: #667eea; margin-bottom: 1rem;"></i>
                <h3 style="color: #667eea;">Historique vide</h3>
                <p style="color: #666;">Aucune donnée historique disponible</p>
            </div>
        """, unsafe_allow_html=True)

# --- BOUCLE PRINCIPALE DE SURVEILLANCE ---
if st.session_state.is_running and TELEGRAM_CONFIGURED:
    # Initialiser la capture vidéo
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        st.error("<i class='fas fa-video-slash'></i> Impossible d'accéder à la caméra")
        st.session_state.is_running = False
        st.stop()
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    # Variables de suivi
    last_alert_time = 0
    fps_counter = 0
    fps_time = time.time()
    alert_history = []
    
    # Placeholder pour les contrôles
    stop_button = st.empty()
    
    try:
        while cap.isOpened() and st.session_state.is_running:
            ret, frame = cap.read()
            if not ret:
                st.error("<i class='fas fa-exclamation-circle'></i> Erreur de capture vidéo")
                break
            
            # Calcul FPS
            fps_counter += 1
            if time.time() - fps_time >= 1:
                current_fps = fps_counter
                fps_counter = 0
                fps_time = time.time()
                
                # Mettre à jour la métrique FPS
                with col4:
                    st.metric("Performance", f"{current_fps} FPS")
            
            # Conversion couleur
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Détection YOLO
            results = model(frame_rgb, conf=conf_level, verbose=False)
            
            # Analyse des objets détectés
            names = model.names
            detected_objects = Counter()
            if results and len(results) > 0 and results[0].boxes is not None:
                detected_objects = Counter([names[int(c)] for c in results[0].boxes.cls])
            
            # Mettre à jour les stats globales
            for obj, count in detected_objects.items():
                st.session_state.detection_stats[obj] += count
            
            # Compter personnes et téléphones
            person_count = detected_objects.get('person', 0)
            phone_count = detected_objects.get('cell phone', 0)
            
            # Mettre à jour les métriques
            with col1:
                st.metric("Personnes détectées", person_count)
            with col2:
                st.metric("Téléphones détectés", phone_count)
            
            # Logique d'alerte
            current_time = time.time()
            should_alert = phone_count > 0
            
            if require_person:
                should_alert = should_alert and person_count > 0
            
            # Vérifier le délai entre alertes
            if should_alert and (current_time - last_alert_time > cooldown):
                # Annoter l'image
                annotated_img = results[0].plot()
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Construire le message d'alerte
                alert_msg = f"""🚨 **ALERTE VISIONGUARD AI** 🚨
                
⏰ **Heure:** {timestamp}
📍 **Détections:**
• 📱 Téléphones: {phone_count}
• 👥 Personnes: {person_count}
• 📦 Total objets: {sum(detected_objects.values())}

📊 **Statistiques:**
{chr(10).join(f'• {obj}: {count}' for obj, count in detected_objects.most_common(5))}
"""
                
                # Envoyer l'alerte Telegram
                success = send_telegram_alert(annotated_img, alert_msg)
                
                if success:
                    # Sauvegarder dans l'historique
                    history_entry = {
                        "Heure": timestamp,
                        "Téléphones": phone_count,
                        "Personnes": person_count,
                        "Objets": dict(detected_objects),
                        "Statut": "✅ Alerte envoyée"
                    }
                    st.session_state.history.insert(0, history_entry)
                    
                    # Mettre à jour l'historique des alertes
                    alert_history.insert(0, {
                        "time": timestamp,
                        "message": f"📱 {phone_count} téléphone(s) détecté(s)"
                    })
                    
                    last_alert_time = current_time
                    
                    # Notification
                    st.toast(f"<i class='fas fa-paper-plane'></i> Alerte envoyée à {timestamp}", icon="📩")
            
            # Mise à jour de l'interface - Flux vidéo
            if results and len(results) > 0:
                annotated_frame = results[0].plot()
                
                # Ajouter des infos sur le frame
                cv2.putText(annotated_frame, f"FPS: {current_fps if 'current_fps' in locals() else 'N/A'}", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(annotated_frame, f"Objets: {len(detected_objects)}", 
                           (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                # Afficher le flux vidéo
                video_container.image(annotated_frame, use_column_width=True, 
                                     caption=f"<i class='fas fa-eye'></i> Surveillance active • {datetime.now().strftime('%H:%M:%S')}")
            
            # Mise à jour de l'interface - Statistiques
            with col_stats:
                if detected_objects:
                    stats_text = "### <i class='fas fa-binoculars'></i> Détections actuelles\n\n"
                    for obj, count in detected_objects.most_common(10):
                        icon = "👤" if obj == "person" else "📱" if "phone" in obj.lower() else "📦"
                        stats_text += f"**{icon} {obj.capitalize()}**: {count}\n"
                    stats_placeholder.markdown(stats_text, unsafe_allow_html=True)
            
            # Mise à jour de l'interface - Alertes récentes
            with col_stats:
                if alert_history:
                    alert_text = "### <i class='fas fa-exclamation-triangle'></i> Dernières alertes\n\n"
                    for alert in alert_history[:3]:
                        alert_text += f"• **{alert['time'][11:]}** - {alert['message']}\n"
                    alert_placeholder.markdown(alert_text, unsafe_allow_html=True)
            
            # Bouton d'arrêt
            if stop_button.button("<i class='fas fa-stop-circle'></i> Arrêter la surveillance", 
                                use_container_width=True, type="secondary"):
                st.session_state.is_running = False
                st.rerun()
            
            time.sleep(0.01)
    
    except Exception as e:
        st.error(f"<i class='fas fa-bug'></i> Erreur dans la boucle de surveillance: {str(e)}")
    
    finally:
        cap.release()
        cv2.destroyAllWindows()

elif st.session_state.is_running and not TELEGRAM_CONFIGURED:
    st.error("""<div style="text-align: center; padding: 2rem;">
               <i class="fas fa-exclamation-circle" style="font-size: 3rem; color: #ff6b6b; margin-bottom: 1rem;"></i>
               <h3 style="color: #ff6b6b;">Configuration Telegram requise</h3>
               <p>Veuillez configurer Telegram pour démarrer la surveillance</p>
               </div>""", unsafe_allow_html=True)
    st.session_state.is_running = False
    st.stop()

else:
    # Écran d'accueil
    st.markdown("""
        <div style="text-align: center; padding: 5rem 2rem; background: white; border-radius: 20px; 
                    box-shadow: 0 15px 40px rgba(0,0,0,0.1); margin-bottom: 3rem;">
            <div class="icon-large pulse-animation">
                <i class="fas fa-play-circle"></i>
            </div>
            <h2 style="color: #667eea; margin-bottom: 1rem; font-family: 'Poppins', sans-serif;">Prêt à démarrer</h2>
            <p style="color: #666; margin-bottom: 2.5rem; font-size: 1.1rem; max-width: 600px; margin-left: auto; margin-right: auto;">
                Configurez vos paramètres dans la barre latérale et cliquez sur "Démarrer" pour lancer la surveillance intelligente
            </p>
            <div style="display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                       color: white; padding: 1rem 2.5rem; border-radius: 50px; font-weight: 600; font-size: 1.1rem; box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);">
                <i class="fas fa-robot"></i> Système en attente
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Features showcase
    st.markdown("### <i class='fas fa-star'></i> Fonctionnalités Premium")
    features_cols = st.columns(3)
    
    features = [
        ("<i class='fas fa-brain'></i>", "Intelligence Artificielle", "Détection avancée avec YOLOv8"),
        ("<i class='fas fa-bolt'></i>", "Temps réel", "Analyse et alertes en temps réel"),
        ("<i class='fas fa-chart-network'></i>", "Multi-détection", "Détection simultanée de multiples objets"),
        ("<i class='fas fa-paper-plane'></i>", "Notifications", "Alertes Telegram instantanées"),
        ("<i class='fas fa-database'></i>", "Historique complet", "Export des données en CSV/Excel"),
        ("<i class='fas fa-shield-alt'></i>", "Sécurisé", "Configuration via secrets Streamlit")
    ]
    
    for i, (icon, title, desc) in enumerate(features):
        with features_cols[i % 3]:
            st.markdown(f"""
                <div class="stat-card" style="text-align: center; padding: 1.5rem;">
                    <div style="font-size: 2.5rem; margin-bottom: 1rem; color: #667eea;">
                        {icon}
                    </div>
                    <h4 style="margin: 0 0 0.5rem 0; color: #2c3e50;">{title}</h4>
                    <p style="margin: 0; color: #666; font-size: 0.9rem;">{desc}</p>
                </div>
            """, unsafe_allow_html=True)

# --- PIED DE PAGE ---
st.markdown("""
    <div style="text-align: center; margin-top: 4rem; padding: 2rem; color: #666; font-size: 0.9rem; 
                border-top: 1px solid rgba(0,0,0,0.1); background: rgba(255,255,255,0.5); border-radius: 15px;">
        <div style="display: flex; justify-content: center; align-items: center; gap: 15px; margin-bottom: 1rem;">
            <i class="fas fa-robot" style="font-size: 1.5rem; color: #667eea;"></i>
            <h3 style="margin: 0; color: #2c3e50; font-family: 'Poppins', sans-serif;">
                VisionGuard <span class="gradient-text">AI Pro</span>
            </h3>
        </div>
        <p style="margin: 0.5rem 0; font-size: 0.95rem;">
            <i class="fas fa-code-branch"></i> Système de surveillance intelligent v2.5
        </p>
        <p style="font-size: 0.8rem; opacity: 0.7; margin-top: 1rem;">
            <i class="fas fa-copyright"></i> 2024 VisionGuard AI • 
            <i class="fas fa-shield-alt"></i> Protection optimisée • 
            <i class="fas fa-rocket"></i> Performance maximale
        </p>
    </div>
""", unsafe_allow_html=True)
