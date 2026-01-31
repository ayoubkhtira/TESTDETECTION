import streamlit as st
from datetime import datetime
import pandas as pd
from collections import Counter
from ultralytics import YOLO
import numpy as np
import io
from PIL import Image

# Configuration
st.set_page_config(page_title="VisionGuard AI - CLOUD OK", page_icon="🤖", layout="wide")

# CSS
st.markdown("""
<style>
.main-header {background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 15px; color: white; margin-bottom: 2rem; text-align: center;}
.metric-card {background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); border-left: 4px solid #667eea;}
.object-badge {display: inline-block; background: #007bff; color: white; padding: 8px 15px; border-radius: 20px; margin: 5px; font-weight: bold;}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header"><h1>🤖 VisionGuard AI Pro - 100% CLOUD</h1><p>Détection YOLO sans OpenCV</p></div>', unsafe_allow_html=True)

# YOLO Model
@st.cache_resource
def load_model():
    return YOLO('yolov8n.pt')

model = load_model()

# Session state
if 'detections' not in st.session_state:
    st.session_state.detections = {'person': 0, 'cell phone': 0, 'car': 0, 'chair': 0, 'total': 0}
if 'results' not in st.session_state:
    st.session_state.results = []

# Fonction détection PIL/YOLO
def detect_image(image_pil):
    # Convertir PIL → numpy pour YOLO
    image_np = np.array(image_pil)
    
    # Détection
    results = model(image_np, verbose=False)
    
    detected = []
    for r in results:
        boxes = r.boxes
        if boxes is not None:
            for box in boxes:
                if float(box.conf[0]) > 0.5:
                    cls_name = model.names[int(box.cls[0])]
                    detected.append(cls_name)
    
    # Compteurs
    counts = Counter(detected)
    for obj, count in counts.items():
        if obj in st.session_state.detections:
            st.session_state.detections[obj] += count
    st.session_state.detections['total'] += len(detected)
    
    st.session_state.results = detected[-10:]
    return results[0].plot()

# Métriques
col1, col2, col3 = st.columns(3)
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

# UPLOAD PRINCIPAL ✅ CLOUD READY
st.markdown("### 📁 **Upload Image pour Détection Instantanée**")

# Streamlit Camera Input (natif, cloud OK)
img_file = st.camera_input("📸 Prendre photo") or st.file_uploader("📁 OU Choisir image", type=['png','jpg','jpeg'])

if img_file:
    image = Image.open(img_file)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.image(image, caption="Image originale", use_column_width=True)
    
    with col2:
        with st.spinner("🔍 YOLO analyse en cours..."):
            annotated = detect_image(image)
            st.image(annotated, caption="✅ Objets détectés", use_column_width=True)

# Résultats
if st.session_state.results:
    st.markdown("### 🎯 **Détections récentes**")
    counts = Counter(st.session_state.results)
    badges = "".join([f'<span class="object-badge">{obj}: {count}</span>' for obj, count in counts.most_common(5)])
    st.markdown(badges, unsafe_allow_html=True)

# Graphique
st.markdown("### 📊 Statistiques")
chart_data = pd.DataFrame({
    'Objet': ['Personnes', 'Téléphones', 'Voitures', 'Chaises'],
    'Nombre': [st.session_state.detections['person'], st.session_state.detections['cell phone'], 
               st.session_state.detections['car'], st.session_state.detections['chair']]
})
st.bar_chart(chart_data.set_index('Objet'))

# Contrôles
if st.button("🔄 Réinitialiser", type="primary", use_container_width=True):
    st.session_state.detections = {'person': 0, 'cell phone': 0, 'car': 0, 'chair': 0, 'total': 0}
    st.session_state.results = []
    st.rerun()

# INFO DÉPLOIEMENT
with st.expander("🚀 Déploiement Streamlit Cloud"):
    st.success("✅ **AUCUN problème d'import !**")
    st.code("""
requirements.txt ULTRA-SIMPLE :
streamlit
ultralytics
pandas
pillow
numpy
    """, language="txt")
    st.balloons()

st.markdown("---")
st.markdown("<div style='text-align:center;color:#666'>🤖 VisionGuard AI v4.0 | Cloud Perfect</div>", unsafe_allow_html=True)
