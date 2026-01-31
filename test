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
    page_icon="🔍",
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
    st.sidebar.warning("⚠️ Configuration Telegram manquante dans les secrets")

# --- CSS POUR THÈME MODERNE ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
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
    
    .alert-badge {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        display: inline-block;
        margin: 0.25rem;
    }
    
    .stat-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #2c3e50 0%, #1a1a2e 100%);
        color: white;
    }
    
    .telegram-status {
        padding: 0.5rem;
        border-radius: 6px;
        margin: 0.5rem 0;
        text-align: center;
        font-weight: 600;
    }
    
    .telegram-success {
        background: linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%);
        color: white;
    }
    
    .telegram-warning {
        background: linear-gradient(135deg, #FF9800 0%, #EF6C00 100%);
        color: white;
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
        # Sauvegarder temporairement l'image
        temp_path = "temp_alert.jpg"
        cv2.imwrite(temp_path, cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR))
        
        # Envoyer via l'API Telegram
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
        with open(temp_path, 'rb') as photo:
            response = requests.post(
                url, 
                data={'chat_id': TELEGRAM_CHAT_ID, 'caption': caption, 'parse_mode': 'Markdown'},
                files={'photo': photo},
                timeout=10
            )
        
        # Nettoyer le fichier temporaire
        if os.path.exists(temp_path):
            os.remove(temp_path)
            
        return response.status_code == 200
        
    except Exception as e:
        st.sidebar.error(f"Erreur Telegram: {str(e)}")
        return False

# --- UI : BARRE LATERALE ---
with st.sidebar:
    st.markdown("""
        <div style="text-align: center; padding: 1rem 0;">
            <h2 style="color: white; margin-bottom: 0.5rem;">🔍 VisionGuard AI</h2>
            <p style="color: #b3b3b3; font-size: 0.9rem;">Système de surveillance intelligent</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Statut Telegram
    with st.expander("🔐 Statut Telegram", expanded=True):
        if TELEGRAM_CONFIGURED:
            st.markdown('<div class="telegram-status telegram-success">✅ Telegram configuré</div>', 
                       unsafe_allow_html=True)
            st.caption(f"Chat ID: {TELEGRAM_CHAT_ID[:4]}...{TELEGRAM_CHAT_ID[-4:]}")
        else:
            st.markdown('<div class="telegram-status telegram-warning">⚠️ Telegram non configuré</div>', 
                       unsafe_allow_html=True)
            st.caption("Ajoutez TELEGRAM_TOKEN et TELEGRAM_CHAT_ID dans les secrets Streamlit")
    
    st.divider()
    
    with st.expander("⚙️ Paramètres de détection", expanded=True):
        conf_level = st.slider("Seuil de confiance", 0.1, 0.9, 0.6, 0.05)
        cooldown = st.slider("Délai entre alertes (s)", 5, 300, 30, 5)
        require_person = st.toggle("Alerte uniquement avec personne", value=True)
        enable_demographics = st.toggle("Analyse démographique", value=False)
    
    st.divider()
    
    # Contrôles
    col1, col2 = st.columns(2)
    with col1:
        if st.button("▶️ Démarrer", use_container_width=True, type="primary", 
                    disabled=not TELEGRAM_CONFIGURED):
            st.session_state.is_running = True
            st.rerun()
    
    with col2:
        if st.button("⏹️ Arrêter", use_container_width=True):
            st.session_state.is_running = False
            st.rerun()
    
    st.divider()
    
    # Statistiques en temps réel
    if st.session_state.detection_stats:
        st.markdown("### 📊 Statistiques actuelles")
        for obj, count in st.session_state.detection_stats.most_common(5):
            col_prog, col_text = st.columns([3, 1])
            with col_prog:
                st.progress(min(count/10, 1.0))
            with col_text:
                st.caption(f"{obj}: {count}")

# --- UI : EN-TÊTE PRINCIPALE ---
st.markdown("""
    <div class="main-header">
        <h1 style="margin: 0; font-size: 2.5rem;">🔍 VisionGuard AI Pro</h1>
        <p style="margin: 0.5rem 0 0 0; font-size: 1.1rem; opacity: 0.9;">
            Système avancé de surveillance et d'analyse en temps réel
        </p>
    </div>
""", unsafe_allow_html=True)

# --- UI : MÉTRIQUES EN TEMPS RÉEL ---
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("👥 Personnes détectées", "0", delta=None)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("📱 Téléphones détectés", "0", delta=None)
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    status = "✅ Active" if TELEGRAM_CONFIGURED else "❌ Inactive"
    st.metric("📡 Notifications", status, delta=None)
    st.markdown('</div>', unsafe_allow_html=True)

with col4:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("⚡ FPS", "0", delta=None)
    st.markdown('</div>', unsafe_allow_html=True)

# --- UI : PRINCIPAL ---
tab1, tab2, tab3 = st.tabs(["🎥 Surveillance", "📊 Analytics", "📋 Historique"])

with tab1:
    col_video, col_stats = st.columns([2, 1])
    
    with col_video:
        st.markdown("### 🔴 Flux vidéo en direct")
        video_feed = st.image([], use_column_width=True, caption="Flux vidéo en attente...")
        
        # Contrôles vidéo
        col_controls = st.columns(3)
        with col_controls[0]:
            if st.button("📸 Capture", use_container_width=True):
                st.session_state.last_capture = datetime.now()
                st.toast("📸 Capture effectuée!", icon="✅")
        with col_controls[1]:
            record = st.toggle("🎥 Enregistrer", value=False, disabled=True)
        with col_controls[2]:
            if st.button("🔄 Réinitialiser stats", use_container_width=True):
                st.session_state.detection_stats = Counter()
                st.rerun()
    
    with col_stats:
        st.markdown("### 📈 Détections en cours")
        stats_placeholder = st.empty()
        stats_placeholder.info("En attente de détections...")
        
        st.markdown("### 🚨 Alertes récentes")
        alert_placeholder = st.empty()
        alert_placeholder.info("Aucune alerte récente")

with tab2:
    st.markdown("### 📊 Analytics approfondis")
    
    if st.session_state.history:
        # Graphique temporel
        df_history = pd.DataFrame(st.session_state.history)
        df_history['Heure'] = pd.to_datetime(df_history['Heure'])
        
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            fig1 = px.line(df_history, x='Heure', y='Personnes', 
                          title="Évolution du nombre de personnes",
                          markers=True)
            st.plotly_chart(fig1, use_container_width=True)
        
        with col_chart2:
            if 'Démographie' in df_history.columns:
                try:
                    demo_data = df_history['Démographie'].explode().value_counts()
                    fig2 = px.pie(values=demo_data.values, names=demo_data.index,
                                 title="Répartition démographique")
                    st.plotly_chart(fig2, use_container_width=True)
                except:
                    st.info("Données démographiques indisponibles")
        
        # Heatmap des objets détectés
        if 'Objets' in df_history.columns:
            st.markdown("### 🔥 Fréquence des objets détectés")
            all_objects = []
            for obj_list in df_history['Objets']:
                if isinstance(obj_list, dict):
                    for obj, count in obj_list.items():
                        all_objects.extend([obj] * count)
            
            if all_objects:
                obj_counts = pd.Series(all_objects).value_counts()
                fig3 = px.bar(x=obj_counts.index, y=obj_counts.values,
                             title="Fréquence des objets détectés",
                             labels={'x': 'Objet', 'y': 'Nombre'})
                st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("Aucune donnée analytique disponible. Lancez la surveillance pour commencer.")

with tab3:
    st.markdown("### 📋 Historique complet")
    if st.session_state.history:
        df_display = pd.DataFrame(st.session_state.history)
        
        # Formater les colonnes
        if 'Objets' in df_display.columns:
            df_display['Objets'] = df_display['Objets'].apply(
                lambda x: ', '.join([f"{k}({v})" for k, v in x.items()]) if isinstance(x, dict) else str(x)
            )
        
        st.dataframe(df_display, use_container_width=True, height=400)
        
        # Boutons d'export
        col_export = st.columns(2)
        with col_export[0]:
            if st.button("📄 Exporter CSV", use_container_width=True):
                csv = df_display.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="Télécharger CSV",
                    data=csv,
                    file_name="visionguard_historique.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        with col_export[1]:
            if st.button("🗑️ Effacer historique", use_container_width=True):
                st.session_state.history = []
                st.rerun()
    else:
        st.info("Aucun historique disponible")

# --- BOUCLE PRINCIPALE DE SURVEILLANCE ---
if st.session_state.is_running and TELEGRAM_CONFIGURED:
    # Initialiser la capture vidéo
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        st.error("❌ Impossible d'accéder à la caméra")
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
    
    # Boucle principale
    try:
        while cap.isOpened() and st.session_state.is_running:
            ret, frame = cap.read()
            if not ret:
                st.error("❌ Erreur de capture vidéo")
                break
            
            # Calcul FPS
            fps_counter += 1
            if time.time() - fps_time >= 1:
                current_fps = fps_counter
                fps_counter = 0
                fps_time = time.time()
                
                # Mettre à jour la métrique FPS
                with col4:
                    st.metric("⚡ FPS", current_fps)
            
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
                st.metric("👥 Personnes détectées", person_count)
            with col2:
                st.metric("📱 Téléphones détectés", phone_count)
            
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
                alert_msg = f"""🚨 **ALERTE VISIONGUARD** 🚨
                
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
                    st.toast(f"🚨 Alerte envoyée à {timestamp}", icon="📩")
            
            # Mise à jour de l'interface - Flux vidéo
            if results and len(results) > 0:
                annotated_frame = results[0].plot()
                
                # Ajouter des infos sur le frame
                cv2.putText(annotated_frame, f"FPS: {current_fps if 'current_fps' in locals() else 'N/A'}", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(annotated_frame, f"Objets: {len(detected_objects)}", 
                           (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                video_feed.image(annotated_frame, use_column_width=True, caption="Flux en direct")
            
            # Mise à jour de l'interface - Statistiques
            with col_stats:
                if detected_objects:
                    stats_text = "### 📈 Détections actuelles\n\n"
                    for obj, count in detected_objects.most_common(10):
                        stats_text += f"**{obj.capitalize()}**: {count}\n"
                    stats_placeholder.markdown(stats_text)
                else:
                    stats_placeholder.info("Aucune détection en cours...")
            
            # Mise à jour de l'interface - Alertes récentes
            with col_stats:
                if alert_history:
                    alert_text = "### 🚨 Dernières alertes\n\n"
                    for alert in alert_history[:3]:
                        alert_text += f"• {alert['time'][11:]} - {alert['message']}\n"
                    alert_placeholder.markdown(alert_text)
            
            # Bouton d'arrêt en bas du flux
            if stop_button.button("⏹️ Arrêter la surveillance", use_container_width=True, type="secondary"):
                st.session_state.is_running = False
                st.rerun()
            
            # Petite pause pour réduire la charge CPU
            time.sleep(0.01)
    
    except Exception as e:
        st.error(f"Erreur dans la boucle de surveillance: {str(e)}")
    
    finally:
        # Nettoyage
        cap.release()
        cv2.destroyAllWindows()

elif st.session_state.is_running and not TELEGRAM_CONFIGURED:
    st.error("❌ Configuration Telegram requise pour démarrer la surveillance")
    st.session_state.is_running = False
    st.stop()

else:
    # Écran d'accueil
    st.markdown("""
        <div style="text-align: center; padding: 4rem 2rem; background: white; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.1);">
            <h2 style="color: #667eea; margin-bottom: 1rem;">🎯 Prêt à démarrer</h2>
            <p style="color: #666; margin-bottom: 2rem;">
                Configurez vos paramètres dans la barre latérale et cliquez sur "Démarrer" pour lancer la surveillance
            </p>
            <div style="font-size: 4rem; color: #764ba2; margin-bottom: 2rem;">🔍</div>
            <div style="display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 0.75rem 2rem; border-radius: 30px; font-weight: 600;">
                Système en attente
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Features showcase
    st.markdown("### 🚀 Fonctionnalités avancées")
    features_cols = st.columns(3)
    
    features = [
        ("🎯 Détection multi-objets", "Détecte et compte tous les objets visibles"),
        ("📱 Détection téléphone", "Alarme spécifique pour téléphones détectés"),
        ("📊 Analytics temps réel", "Graphiques et statistiques en direct"),
        ("🔔 Alertes Telegram", "Notifications instantanées avec photos"),
        ("💾 Historique complet", "Export CSV des détections"),
        ("⚡ Performances optimisées", "Traitement en temps réel rapide")
    ]
    
    for i, (title, desc) in enumerate(features):
        with features_cols[i % 3]:
            st.markdown(f"""
                <div class="stat-card">
                    <h4 style="margin: 0 0 0.5rem 0; color: #667eea;">{title}</h4>
                    <p style="margin: 0; color: #666; font-size: 0.9rem;">{desc}</p>
                </div>
            """, unsafe_allow_html=True)

# --- PIED DE PAGE ---
st.markdown("""
    <div style="text-align: center; margin-top: 3rem; padding: 1.5rem; color: #666; font-size: 0.9rem; border-top: 1px solid #eee;">
        <p>🔍 <strong>VisionGuard AI Pro</strong> | Système de surveillance intelligent v2.0</p>
        <p style="font-size: 0.8rem; opacity: 0.7;">
            Protection optimisée avec YOLOv8 | Notifications Telegram intégrées
        </p>
    </div>
""", unsafe_allow_html=True)
