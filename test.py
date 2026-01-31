import streamlit as st
import cv2
import time
import numpy as np
from datetime import datetime
import pandas as pd
from collections import Counter
import plotly.express as px
import plotly.graph_objects as go

# Configuration de la page
st.set_page_config(
    page_title="VisionGuard AI - Détection Automatique",
    page_icon="🎥",
    layout="wide",
    initial_sidebar_state="collapsed"  # Cache la sidebar pour plus d'espace
)

# CSS minimaliste
st.markdown("""
<style>
    .main-container {
        max-width: 1400px;
        margin: 0 auto;
    }
    .video-container {
        background: #1a1a1a;
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 20px;
        text-align: center;
    }
    .stats-container {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
    }
    .object-counter {
        display: inline-block;
        background: #007bff;
        color: white;
        padding: 5px 15px;
        border-radius: 20px;
        margin: 5px;
        font-weight: bold;
    }
    .alert-badge {
        background: #dc3545;
        color: white;
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: bold;
        animation: blink 1s infinite;
    }
    @keyframes blink {
        50% { opacity: 0.7; }
    }
</style>
""", unsafe_allow_html=True)

# Initialisation de l'état de session
if 'detection_stats' not in st.session_state:
    st.session_state.detection_stats = Counter()
if 'last_telegram_send' not in st.session_state:
    st.session_state.last_telegram_send = 0
if 'detection_history' not in st.session_state:
    st.session_state.detection_history = []

# Titre principal
st.title("🎥 VisionGuard AI - Détection en Temps Réel")
st.markdown("Système de surveillance automatique avec envoi Telegram")

# Fonction pour envoyer à Telegram
def send_to_telegram(image_np, caption):
    """Envoie une image à Telegram"""
    try:
        TELEGRAM_TOKEN = st.secrets["TELEGRAM_TOKEN"]
        TELEGRAM_CHAT_ID = st.secrets["TELEGRAM_CHAT_ID"]
        
        # Sauvegarder l'image temporairement
        import tempfile
        import requests
        
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
            cv2.imwrite(tmp.name, cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR))
            
            # Envoyer à Telegram
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
            files = {'photo': open(tmp.name, 'rb')}
            data = {'chat_id': TELEGRAM_CHAT_ID, 'caption': caption}
            
            response = requests.post(url, files=files, data=data)
            return response.status_code == 200
    except Exception as e:
        st.error(f"Erreur Telegram: {str(e)}")
        return False

# Fonction principale de détection
def run_detection():
    """Exécute la détection YOLO en continu"""
    
    # Charger le modèle YOLO
    try:
        from ultralytics import YOLO
        model = YOLO("yolov8n.pt")
    except ImportError:
        st.error("⚠️ Le module YOLO n'est pas installé. Installez avec: pip install ultralytics")
        st.stop()
    
    # Initialiser la caméra
    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            st.error("❌ Impossible d'accéder à la caméra")
            st.stop()
        
        # Ajuster la résolution
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        # Placeholders pour l'affichage
        video_placeholder = st.empty()
        stats_placeholder = st.empty()
        time_placeholder = st.empty()
        
        # Boucle principale
        while True:
            # Lire l'image de la caméra
            ret, frame = cap.read()
            if not ret:
                st.warning("⚠️ Problème avec la caméra")
                break
            
            # Convertir en RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Détection YOLO
            results = model(frame_rgb, conf=0.5)
            
            # Analyser les résultats
            detected_objects = Counter()
            if results and len(results) > 0:
                names = model.names
                boxes = results[0].boxes
                
                if boxes is not None:
                    for box in boxes:
                        class_id = int(box.cls[0])
                        object_name = names[class_id]
                        detected_objects[object_name] += 1
            
            # Mettre à jour les statistiques
            for obj, count in detected_objects.items():
                st.session_state.detection_stats[obj] += count
            
            # Enregistrer dans l'historique
            current_time = datetime.now()
            st.session_state.detection_history.append({
                'timestamp': current_time,
                'objects': dict(detected_objects)
            })
            
            # Envoyer à Telegram toutes les 5 secondes si des objets sont détectés
            current_time_ts = time.time()
            if current_time_ts - st.session_state.last_telegram_send > 5 and detected_objects:
                # Créer un caption détaillé
                caption = f"🔍 Détection VisionGuard\n"
                caption += f"📅 {current_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                caption += f"📊 Statistiques:\n"
                
                for obj, count in detected_objects.most_common(5):
                    caption += f"• {obj}: {count}\n"
                
                # Envoyer l'image avec les annotations
                if results and len(results) > 0:
                    annotated_frame = results[0].plot()
                    success = send_to_telegram(annotated_frame, caption)
                    
                    if success:
                        st.success("📤 Image envoyée à Telegram")
                        st.session_state.last_telegram_send = current_time_ts
            
            # Afficher la vidéo avec les détections
            if results and len(results) > 0:
                annotated_frame = results[0].plot()
                video_placeholder.image(annotated_frame, channels="BGR", 
                                       caption=f"Détection en temps réel - {current_time.strftime('%H:%M:%S')}")
            else:
                video_placeholder.image(frame_rgb, 
                                       caption=f"Surveillance active - {current_time.strftime('%H:%M:%S')}")
            
            # Afficher les statistiques
            with stats_placeholder.container():
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("### 👥 Personnes")
                    person_count = st.session_state.detection_stats.get('person', 0)
                    st.markdown(f"<h1 style='color: #007bff; text-align: center;'>{person_count}</h1>", 
                               unsafe_allow_html=True)
                
                with col2:
                    st.markdown("### 📱 Téléphones")
                    phone_count = st.session_state.detection_stats.get('cell phone', 0)
                    st.markdown(f"<h1 style='color: #28a745; text-align: center;'>{phone_count}</h1>", 
                               unsafe_allow_html=True)
                
                with col3:
                    st.markdown("### 🚨 Total objets")
                    total_count = sum(st.session_state.detection_stats.values())
                    st.markdown(f"<h1 style='color: #dc3545; text-align: center;'>{total_count}</h1>", 
                               unsafe_allow_html=True)
            
            # Afficher les objets détectés individuellement
            st.markdown("### 📊 Objets détectés (en temps réel)")
            
            if detected_objects:
                # Créer des badges pour chaque objet
                html_badges = ""
                for obj, count in detected_objects.most_common(10):
                    color = "#007bff" if obj == "person" else "#28a745" if "phone" in obj else "#6c757d"
                    html_badges += f"""
                    <span style="
                        background: {color};
                        color: white;
                        padding: 8px 15px;
                        border-radius: 20px;
                        margin: 5px;
                        display: inline-block;
                        font-weight: bold;
                    ">
                        {obj}: {count}
                    </span>
                    """
                st.markdown(html_badges, unsafe_allow_html=True)
            else:
                st.info("Aucun objet détecté pour le moment")
            
            # Rafraîchir l'affichage
            time_placeholder.markdown(f"**Dernière mise à jour:** {current_time.strftime('%H:%M:%S')}")
            time.sleep(0.1)  # Petite pause pour réduire la charge CPU
            
    except Exception as e:
        st.error(f"❌ Erreur: {str(e)}")
    finally:
        if 'cap' in locals():
            cap.release()
        cv2.destroyAllWindows()

# Fonction pour afficher les statistiques détaillées
def show_detailed_stats():
    """Affiche les statistiques détaillées des détections"""
    
    if not st.session_state.detection_stats:
        st.info("Aucune donnée de détection disponible")
        return
    
    st.markdown("---")
    st.markdown("## 📈 Statistiques détaillées")
    
    # Top 10 des objets détectés
    top_objects = st.session_state.detection_stats.most_common(10)
    
    # Créer un graphique
    objects, counts = zip(*top_objects) if top_objects else ([], [])
    
    if objects:
        fig = px.bar(
            x=objects, 
            y=counts,
            title="Top 10 des objets détectés",
            labels={'x': 'Objet', 'y': 'Nombre'},
            color=counts,
            color_continuous_scale='Viridis'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Tableau des statistiques
    df_stats = pd.DataFrame(
        list(st.session_state.detection_stats.items()),
        columns=['Objet', 'Nombre']
    )
    st.dataframe(df_stats.sort_values('Nombre', ascending=False), 
                use_container_width=True)

# Vérifier si Telegram est configuré
try:
    TELEGRAM_TOKEN = st.secrets["TELEGRAM_TOKEN"]
    TELEGRAM_CHAT_ID = st.secrets["TELEGRAM_CHAT_ID"]
    telegram_configured = True
    st.success("✅ Telegram configuré avec succès")
except:
    telegram_configured = False
    st.warning("⚠️ Telegram non configuré. Ajoutez TELEGRAM_TOKEN et TELEGRAM_CHAT_ID dans les secrets.")

# Contrôles de l'application
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🔄 Redémarrer la détection", type="primary"):
        st.rerun()

with col2:
    if st.button("📊 Afficher statistiques"):
        st.session_state.show_stats = True

with col3:
    if st.button("🧹 Réinitialiser compteurs"):
        st.session_state.detection_stats = Counter()
        st.session_state.detection_history = []
        st.success("Compteurs réinitialisés")
        st.rerun()

# Lancer la détection automatiquement
st.markdown("---")
st.markdown("## 🎥 Flux de détection en direct")

# Afficher un indicateur de statut
status_col1, status_col2, status_col3 = st.columns(3)

with status_col1:
    st.markdown("**🔴 Caméra:** Activée")

with status_col2:
    st.markdown("**🤖 YOLO:** En cours...")

with status_col3:
    next_telegram = max(0, 5 - (time.time() - st.session_state.last_telegram_send))
    st.markdown(f"**📤 Prochain envoi Telegram:** {int(next_telegram)}s")

# Exécuter la détection
run_detection()

# Afficher les statistiques détaillées si demandé
if st.session_state.get('show_stats', False):
    show_detailed_stats()

# Informations système
st.markdown("---")
st.markdown("### ℹ️ Informations techniques")

info_col1, info_col2, info_col3 = st.columns(3)

with info_col1:
    st.markdown("**Version:** 2.0")
    st.markdown("**Modèle:** YOLOv8 Nano")

with info_col2:
    st.markdown("**Fréquence détection:** Temps réel")
    st.markdown("**Fréquence Telegram:** 5 secondes")

with info_col3:
    st.markdown("**Statut Telegram:** " + ("✅ Connecté" if telegram_configured else "❌ Non configuré"))
    st.markdown(f"**Détections totales:** {sum(st.session_state.detection_stats.values())}")

# Pied de page
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666; padding: 20px;'>"
    "🎥 VisionGuard AI v2.0 | Détection automatique | Envoi Telegram"
    "</div>",
    unsafe_allow_html=True
)
