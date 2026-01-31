import streamlit as st
import time
from datetime import datetime
import pandas as pd
import numpy as np
import cv2
from ultralytics import YOLO
from collections import Counter

# Configuration
st.set_page_config(page_title="VisionGuard AI - CLOUD", page_icon="🤖", layout="wide")

# CSS
st.markdown("""
<style>
.main-header {background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 15px; color: white; margin-bottom: 2rem; text-align: center;}
.metric-card {background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); border-left: 4px solid #667eea; margin-bottom: 1rem;}
.object-badge {display: inline-block; background: #007bff; color: white; padding: 8px 15px; border-radius: 20px; margin: 5px; font-weight: bold;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header"><h1>🤖 VisionGuard AI Pro - CLOUD OK</h1><p>Upload image/vidéo + YOLO temps réel</p></div>', unsafe_allow_html=True)

# Charger YOLO
@st.cache_resource
def load_yolo():
    return YOLO('yolov8n.pt')

model = load_yolo()

# Session state
if 'detections' not in st.session_state:
    st.session_state.detections = {'person': 0, 'cell phone': 0, 'car': 0, 'chair': 0, 'total': 0}
if 'last_results' not in st.session_state:
    st.session_state.last_results = []

# Fonction détection
def detect_objects(image):
    results = model(image, verbose=False)
    
    detected = []
    for r in results:
        boxes = r.boxes
        if boxes is not None:
            for box in boxes:
                if float(box.conf[0]) > 0.5:
                    cls_name = model.names[int(box.cls[0])]
                    detected.append(cls_name)
    
    # Update compteurs
    counts = Counter(detected)
    for obj, count in counts.items():
        if obj in st.session_state.detections:
            st.session_state.detections[obj] += count
    st.session_state.detections['total'] += len(detected)
    
    st.session_state.last_results = detected[-10:]
    return results[0].plot()

# Métriques
col1, col2, col3 = st.columns(3)
with col1: st.metric("👥 Personnes", st.session_state.detections['person'])
with col2: st.metric("📱 Téléphones", st.session_state.detections['cell phone'])
with col3: st.metric("🚨 Total", st.session_state.detections['total'])

# UPLOAD PRINCIPAL ☁️ CLOUD READY
st.markdown("### 📁 **Upload Image/Vidéo pour Détection**")
uploaded_file = st.file_uploader("Choisir fichier", type=['png','jpg','jpeg','mp4','avi','mov'])

if uploaded_file is not None:
    if uploaded_file.type.startswith('image/'):
        # Image
        image_bytes = uploaded_file.read()
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        with st.spinner("🔍 Détection YOLO en cours..."):
            annotated = detect_objects(image)
        
        st.image(annotated, caption="✅ Détection terminée", use_column_width=True)
        
    elif uploaded_file.type.startswith('video/'):
        # Vidéo - preview frame par frame
        tfile = tempfile.NamedTemporaryFile(delete=False)
        tfile.write(uploaded_file.read())
        cap = cv2.VideoCapture(tfile.name)
        
        st.video(uploaded_file)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        st.info(f"🎥 {frame_count} frames - Analyse frame par frame disponible")
        
        cap.release()

# Résultats live
if st.session_state.last_results:
    st.markdown("### 🎯 **Objets détectés récemment**")
    counts = Counter(st.session_state.last_results)
    badges = "".join([f'<span class="object-badge">{obj}: {count}</span>' for obj, count in counts.most_common(5)])
    st.markdown(badges, unsafe_allow_html=True)

# Graphique
st.markdown("### 📊 Statistiques")
chart_data = pd.DataFrame({
    'Objet': ['Personnes', 'Téléphones', 'Voitures', 'Chaises'],
    'Nombre': [st.session_state.detections[k] for k in ['person', 'cell phone', 'car', 'chair']]
})
st.bar_chart(chart_data.set_index('Objet'))

# Contrôles
if st.button("🔄 Réinitialiser", type="primary"):
    st.session_state.detections = {'person': 0, 'cell phone': 0, 'car': 0, 'chair': 0, 'total': 0}
    st.session_state.last_results = []
    st.rerun()

# Info
with st.expander("ℹ️ Déploiement Cloud"):
    st.success("✅ **100% Streamlit Cloud compatible**")
    st.code("""
requirements.txt:
streamlit
ultralytics
opencv-python-headless
pandas
numpy
    """)

st.markdown("---")
st.markdown("<div style='text-align:center;color:#666'>🤖 VisionGuard AI v3.1 | Cloud Ready</div>", unsafe_allow_html=True)
