import streamlit as st
import time
from datetime import datetime
import pandas as pd
import numpy as np
import av
import cv2
from ultralytics import YOLO
import numpy as np
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration

# Configuration de base
st.set_page_config(
    page_title="VisionGuard AI - Détection Intelligente CLOUD",
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
    .object-badge {
        display: inline-block;
        background: #007bff;
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
    <h1>🤖 VisionGuard AI Pro - CLOUD READY</h1>
    <p>✅ Détection YOLO temps réel sur Streamlit Cloud</p>
</div>
""", unsafe_allow_html=True)

# Charger YOLO
@st.cache_resource
def load_yolo_model():
    model = YOLO('yolov8n.pt')
    return model

model = load_yolo_model()

# Initialisation session state
if 'detections' not in st.session_state:
    st.session_state.detections = {'person': 0, 'cell phone': 0, 'car': 0, 'chair': 0, 'total': 0}
if 'live_detections' not in st.session_state:
    st.session_state.live_detections = []
if 'frame_count' not in st.session_state:
    st.session_state.frame_count = 0

# Fonction de détection
def video_frame_callback(frame):
    img = frame.to_ndarray(format="bgr24")
    
    # Détection YOLO
    results = model(img, verbose=False)
    
    # Compter les objets
    detected_objects = []
    for r in results:
        boxes = r.boxes
        if boxes is not None:
            for box in boxes:
                conf = float(box.conf[0])
                if conf > 0.5:
                    cls_id = int(box.cls[0])
                    class_name = model.names[cls_id]
                    detected_objects.append(class_name)
    
    # Mettre à jour compteurs
    from collections import Counter
    counts = Counter(detected_objects)
    for obj, count in counts.items():
        if obj in st.session_state.detections:
            st.session_state.detections[obj] += count
    st.session_state.detections['total'] += len(detected_objects)
    
    st.session_state.live_detections = detected_objects[-20:]  # 20 dernières détections
    st.session_state.frame_count += 1
    
    # Frame annoté
    annotated_frame = results[0].plot()
    return av.VideoFrame.from_ndarray(annotated_frame, format="bgr24")

# RTC Configuration pour Streamlit Cloud
RTC_CONFIGURATION = RTCConfiguration({
    "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
})

# Métriques
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
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("📊 Frames", st.session_state.frame_count)
    st.markdown('</div>', unsafe_allow_html=True)

# 🎥 WEBCAM STREAMLIT CLOUD ✅
st.markdown("### 🎥 **Webcam Live Détection** (Fonctionne sur Cloud !)")

# Alternative 1 : Webcam live avec streamlit-webrtc
st.info("👆 **Cliquez START dans le lecteur vidéo** pour activer votre webcam")

webrtc_ctx = webrtc_streamer(
    key="detection",
    mode=WebRtcMode.SENDRECV,
    rtc_configuration=RTC_CONFIGURATION,
    video_frame_callback=video_frame_callback,
    media_stream_constraints={
        "video": {
            "width": {"ideal": 640},
            "height": {"ideal": 480}
        }
    }
)

# Alternative 2 : Upload image/vidéo
st.markdown("### 📁 **OU Upload Image/Vidéo**")
col_upload1, col_upload2 = st.columns([3,1])

with col_upload1:
    uploaded_file = st.file_uploader(
        "Choisir image/vidéo", 
        type=['png','jpg','jpeg','mp4','avi','mov'],
        help="Upload pour analyse immédiate"
    )

with col_upload2:
    if st.button("🔍 Analyser maintenant", type="primary"):
        st.session_state.analyze_upload = True

if uploaded_file and st.session_state.get('analyze_upload', False):
    if uploaded_file.type.startswith('image/'):
        image = np.frombuffer(uploaded_file.read(), np.uint8)
        image = cv2.imdecode(image, cv2.IMREAD_COLOR)
        
        results = model(image, verbose=False)
        annotated_image = results[0].plot()
        
        st.image(annotated_image, caption="Détection terminée", use_column_width=True)
        
        # Compter objets
        detected = []
        for r in results:
            boxes = r.boxes
            if boxes is not None:
                for box in boxes:
                    if float(box.conf[0]) > 0.5:
                        detected.append(model.names[int(box.cls[0])])
        
        st.success(f"🎯 **{len(detected)} objets détectés**")
        if detected:
            from collections import Counter
            counts = Counter(detected)
            for obj, count in counts.items():
                st.markdown(f'<span class="object-badge">{obj}: {count}</span>', unsafe_allow_html=True)

# Objets détectés en live
if st.session_state.live_detections:
    st.markdown("### 🎯 **Détections Live**")
    from collections import Counter
    live_counts = Counter(st.session_state.live_detections)
    badges_html = ""
    for obj, count in live_counts.most_common(5):
        badges_html += f'<span class="object-badge">{obj}: {count}</span>'
    st.markdown(badges_html, unsafe_allow_html=True)

# Graphique
st.markdown("### 📈 **Statistiques**")
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

# Boutons contrôle
col_btn1, col_btn2, col_btn3 = st.columns(3)
if col_btn1.button("🔄 Réinitialiser", use_container_width=True):
    st.session_state.detections = {'person': 0, 'cell phone': 0, 'car': 0, 'chair': 0, 'total': 0}
    st.session_state.live_detections = []
    st.session_state.frame_count = 0
    st.rerun()

# Info déploiement
with st.expander("🚀 **Déploiement Cloud - Installation**"):
    st.success("✅ **Prêt pour Streamlit Cloud !**")
    st.code("""
pip install streamlit ultralytics av opencv-python streamlit-webrtc
    """)
    st.info("""
**Fonctionnalités CLOUD :**
✅ Webcam live (bouton START)
✅ Upload image/vidéo  
✅ YOLOv8 temps réel
✅ Métriques live
✅ HTTPS automatique
    """)

st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>"
    "🤖 VisionGuard AI Pro v3.0 | Cloud Ready | YOLOv8 Live"
    "</div>", 
    unsafe_allow_html=True
)
