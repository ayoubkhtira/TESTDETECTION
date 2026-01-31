import streamlit as st
import time
from datetime import datetime
import pandas as pd
import numpy as np
import threading
import queue

# Configuration de base
st.set_page_config(
    page_title="VisionGuard AI - Détection Intelligente",
    page_icon="🤖",
    layout="wide"
)

# CSS personnalisé (gardé identique)
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

# Vérifier les dépendances
try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
    st.error("❌ OpenCV requis pour la caméra. Installez avec : `pip install opencv-python`")
    st.stop()

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
    model = YOLO('yolov8n.pt')  # Modèle YOLO pré-entraîné
except ImportError:
    YOLO_AVAILABLE = False
    st.error("❌ YOLO requis. Installez avec : `pip install ultralytics`")
    st.stop()

# Vérifier Telegram
try:
    TELEGRAM_TOKEN = st.secrets["TELEGRAM_TOKEN"]
    TELEGRAM_CHAT_ID = st.secrets["TELEGRAM_CHAT_ID"]
    TELEGRAM_CONFIGURED = True
except:
    TELEGRAM_CONFIGURED = False

# Initialisation session state
if 'detections' not in st.session_state:
    st.session_state.detections = {'person': 0, 'cell phone': 0, 'car': 0, 'chair': 0, 'total': 0}
if 'history' not in st.session_state:
    st.session_state.history = []
if 'last_telegram_send' not in st.session_state:
    st.session_state.last_telegram_send = 0
if 'camera_active' not in st.session_state:
    st.session_state.camera_active = False
if 'frame_queue' not in st.session_state:
    st.session_state.frame_queue = queue.Queue(maxsize=1)
if 'detection_results' not in st.session_state:
    st.session_state.detection_results = []

# Variables globales pour le thread caméra
camera_thread = None
stop_camera = threading.Event()

def camera_thread_function():
    """Thread pour capturer la vidéo de la caméra"""
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    while not stop_camera.is_set():
        ret, frame = cap.read()
        if not ret:
            break
            
        # Redimensionner pour YOLO
        frame_resized = cv2.resize(frame, (640, 640))
        
        # Détection YOLO
        results = model(frame_resized, verbose=False)
        
        # Extraire les détections
        detected_objects = []
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    cls_id = int(box.cls[0])
                    conf = float(box.conf[0])
                    if conf > 0.5:  # Seuil de confiance
                        class_name = model.names[cls_id]
                        detected_objects.append(class_name)
        
        # Mettre à jour les compteurs
        for obj in detected_objects:
            if obj in st.session_state.detections:
                st.session_state.detections[obj] += 1
            st.session_state.detections['total'] += 1
        
        # Stocker le frame annoté et les résultats
        annotated_frame = results[0].plot()
        annotated_frame = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
        
        try:
            st.session_state.frame_queue.put_nowait((annotated_frame, detected_objects))
        except queue.Full:
            pass  # Ignore si queue pleine
        
        st.session_state.detection_results = detected_objects[-10:]  # Garde les 10 dernières
        time.sleep(0.1)  # 10 FPS max
    
    cap.release()

def send_to_telegram():
    """Envoi simulé à Telegram (à implémenter avec requests)"""
    current_time = time.time()
    if current_time - st.session_state.last_telegram_send > 10:
        timestamp = datetime.now().strftime("%H:%M:%S")
        message = f"🔍 VisionGuard AI\n🕐 {timestamp}\n👥 Personnes: {st.session_state.detections['person']}\n📱 Total: {st.session_state.detections['total']}"
        
        st.session_state.history.append({
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'message': f"📤 Alert envoyé - {st.session_state.detections['total']} objets"
        })
        st.session_state.last_telegram_send = current_time
        st.rerun()
    return False

# Interface principale
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("👥 Personnes", st.session_state.detections['person'])
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("📱 Téléphones", st.session_state.detections['cell phone'])
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("🚨 Total", st.session_state.detections['total'])
    st.markdown('</div>', unsafe_allow_html=True)

with col4:
    status = "🟢 Active" if TELEGRAM_CONFIGURED else "🔴 Configurer"
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("📤 Telegram", status)
    st.markdown('</div>', unsafe_allow_html=True)

# Contrôles caméra
st.markdown("### 🎥 Caméra & Détection Live")
col_btn1, col_btn2, col_btn3 = st.columns(3)

if col_btn1.button("▶️ **DÉMARRER Caméra**", use_container_width=True, type="primary"):
    if not st.session_state.camera_active:
        st.session_state.camera_active = True
        stop_camera.clear()
        camera_thread = threading.Thread(target=camera_thread_function, daemon=True)
        camera_thread.start()
        st.rerun()

if col_btn2.button("⏹️ **ARRÊTER Caméra**", use_container_width=True):
    st.session_state.camera_active = False
    stop_camera.set()
    st.rerun()

if col_btn3.button("🔄 Réinitialiser", use_container_width=True):
    st.session_state.detections = {'person': 0, 'cell phone': 0, 'car': 0, 'chair': 0, 'total': 0}
    st.session_state.detection_results = []
    st.rerun()

# Affichage vidéo
video_container = st.empty()
if st.session_state.camera_active:
    try:
        frame, detected_objects = st.session_state.frame_queue.get_nowait()
        st.session_state.last_frame = frame
        st.session_state.last_detected = detected_objects
    except queue.Empty:
        frame = getattr(st.session_state, 'last_frame', None)
        detected_objects = getattr(st.session_state, 'last_detected', [])
    
    if frame is not None:
        st.image(frame, channels="RGB", use_column_width=True)
        
        if detected_objects:
            badges_html = ""
            from collections import Counter
            counts = Counter(detected_objects)
            for obj, count in counts.most_common(5):
                badges_html += f'<span class="object-badge">{obj}: {count}</span>'
            st.markdown(f"**🎯 {len(detected_objects)} objets détectés maintenant :**")
            st.markdown(badges_html, unsafe_allow_html=True)
    else:
        st.warning("📹 Connexion caméra en cours...")
else:
    video_container.markdown("""
    <div class="video-container">
        <div style="font-size: 4rem; color: #666;">📹</div>
        <div style="color: white; font-size: 1.2rem; margin-top: 10px;">
            Cliquez sur "DÉMARRER Caméra" pour commencer
        </div>
    </div>
    """, unsafe_allow_html=True)

# Statistiques
st.markdown("### 📊 Statistiques Détections")
chart_data = pd.DataFrame({
    'Objet': ['Personnes', 'Téléphones', 'Voitures', 'Chaises'],
    'Nombre': [
        st.session_state.detections['person'],
        st.session_state.detections['cell phone'],
        st.session_state.detections['car'],
        st.session_state.detections['chair']
    ]
})
st.bar_chart(chart_data.set_index('Objet'), use_container_width=True)

# Historique
if st.session_state.history:
    st.markdown("### 📋 Dernières alertes")
    for entry in st.session_state.history[-3:]:
        st.info(f"🕐 {entry['timestamp']} - {entry['message']}")

# Info système
with st.expander("ℹ️ Système & Installation"):
    st.success("✅ **Dépendances OK** : OpenCV + YOLOv8")
    st.info("""
    **Installation requise :**
    ```bash
    pip install streamlit opencv-python ultralytics
    ```
    
    **Caméra :** Webcam par défaut (index 0)
    **Modèle :** YOLOv8n (nano) - 80 classes COCO
    **FPS :** ~10 FPS optimisé
    """)

st.markdown("---")
st.markdown("<div style='text-align: center; color: #666;'>🤖 VisionGuard AI Pro v2.2 | Détection temps réel</div>", unsafe_allow_html=True)
