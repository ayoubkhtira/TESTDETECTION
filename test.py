import streamlit as st
import pandas as pd
from datetime import datetime
from collections import Counter
import numpy as np

# Configuration
st.set_page_config(page_title="VisionGuard AI - CLOUD 100%", page_icon="🤖", layout="wide")

# CSS moderne
st.markdown("""
<style>
.main-header {background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 15px; color: white; margin-bottom: 2rem; text-align: center;}
.metric-card {background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); border-left: 4px solid #667eea; margin-bottom: 1rem;}
.detection-badge {display: inline-block; background: #28a745; color: white; padding: 8px 15px; border-radius: 20px; margin: 5px; font-weight: bold;}
.warning-badge {background: #ffc107; color: #212529;}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>🤖 VisionGuard AI Pro</h1>
    <p>✅ 100% Streamlit Cloud - Simulation intelligente</p>
</div>
""", unsafe_allow_html=True)

# Session state
if 'detections' not in st.session_state:
    st.session_state.detections = {'person': 0, 'cell phone': 0, 'car': 0, 'chair': 0, 'total': 0}
if 'history' not in st.session_state:
    st.session_state.history = []
if 'detection_log' not in st.session_state:
    st.session_state.detection_log = []

# Simulation intelligente YOLO
def simulate_yolo_detection():
    """Simulation réaliste de détection YOLO"""
    import random
    import time
    
    objects = [
        ('person', 0.45),
        ('cell phone', 0.25), 
        ('car', 0.15),
        ('chair', 0.10),
        ('laptop', 0.05)
    ]
    
    detected = []
    for obj, prob in objects:
        if random.random() < prob:
            count = random.randint(1, 3)
            detected.extend([obj] * count)
    
    # Update compteurs
    for obj in detected:
        if obj in st.session_state.detections:
            st.session_state.detections[obj] += 1
        else:
            st.session_state.detections[obj] = 1
    st.session_state.detections['total'] += len(detected)
    
    # Log
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.detection_log.append({
        'time': timestamp,
        'objects': detected,
        'count': len(detected)
    })
    
    return detected

# Métriques principales
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("👥 Personnes", st.session_state.detections['person'])
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("📱 Téléphones", st.session_state.detections.get('cell phone', 0))
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("🚨 Total", st.session_state.detections['total'])
    st.markdown('</div>', unsafe_allow_html=True)

with col4:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("📊 Sessions", len(st.session_state.history))
    st.markdown('</div>', unsafe_allow_html=True)

# Interface principale
st.markdown("### 🎥 **Système de détection actif**")

col_btn1, col_btn2 = st.columns(2)
with col_btn1:
    if st.button("▶️ **DÉMARRER Détection Auto**", type="primary", use_container_width=True):
        st.session_state.auto_detect = True
        st.rerun()

with col_btn2:
    if st.button("🔍 **Analyse Manuelle**", use_container_width=True):
        detected = simulate_yolo_detection()
        st.session_state.auto_detect = False
        st.rerun()

# Détection automatique
if st.session_state.get('auto_detect', False):
    # Timer simulation
    if 'last_detection' not in st.session_state:
        st.session_state.last_detection = 0
    
    current_time = pd.Timestamp.now().timestamp()
    if current_time - st.session_state.last_detection > 3:  # Toutes les 3s
        detected = simulate_yolo_detection()
        st.session_state.last_detection = current_time
        
        # Vidéo simulée
        st.success(f"🎯 **{len(detected)} objets détectés**")
        
        if detected:
            counts = Counter(detected)
            badges = "".join([f'<span class="detection-badge">{obj}: {count}</span>' 
                            for obj, count in counts.items()])
            st.markdown(badges, unsafe_allow_html=True)

# Upload images (fonctionne toujours)
st.markdown("### 📁 **Upload Images (Compatible Cloud)**")
uploaded_file = st.camera_input("📸 Webcam") or st.file_uploader("📁 Images", type=['png','jpg','jpeg'])

if uploaded_file:
    image = st.image(uploaded_file, caption="✅ Image reçue - Analyse simulée", use_column_width=True)
    
    # Simulation détection sur upload
    detected = simulate_yolo_detection()
    st.balloons()
    
    st.markdown("### 🎯 **Objets détectés sur votre image**")
    counts = Counter(detected)
    badges = "".join([f'<span class="detection-badge">{obj}: {count}</span>' 
                    for obj, count in counts.items()])
    st.markdown(badges, unsafe_allow_html=True)

# Graphique
st.markdown("### 📈 **Statistiques Live**")
chart_data = pd.DataFrame({
    'Objet': ['Personnes', 'Téléphones', 'Voitures', 'Chaises'],
    'Nombre': [
        st.session_state.detections.get('person', 0),
        st.session_state.detections.get('cell phone', 0),
        st.session_state.detections.get('car', 0),
        st.session_state.detections.get('chair', 0)
    ]
})
st.bar_chart(chart_data.set_index('Objet'), use_container_width=True)

# Historique
if st.session_state.detection_log:
    st.markdown("### 📋 **Détections récentes**")
    for log in st.session_state.detection_log[-5:]:
        obj_list = ", ".join(log['objects'])
        st.caption(f"🕐 {log['time']} - {obj_list} ({log['count']} objs)")

# Contrôles
if st.button("🔄 **Réinitialiser Tout**", type="secondary", use_container_width=True):
    st.session_state.detections = {'person': 0, 'cell phone': 0, 'car': 0, 'chair': 0, 'total': 0}
    st.session_state.detection_log = []
    st.session_state.history = []
    if 'auto_detect' in st.session_state:
        st.session_state.auto_detect = False
    st.rerun()

# INFO DÉPLOIEMENT ✅
with st.expander("🚀 **Déploiement Parfait**"):
    st.success("✅ **AUCUNE dépendance externe !**")
    st.code("""
requirements.txt MINIMAL :
streamlit
pandas
numpy
    """, language="txt")
    st.info("""
✅ Déploiement instantané
✅ Webcam input (camera_input)
✅ Upload images  
✅ Métriques live
✅ 100% stable Cloud
    """)

st.markdown("---")
st.markdown("<div style='text-align:center;color:#666'>🤖 VisionGuard AI v5.0 | Cloud Perfect | No Dependencies</div>", unsafe_allow_html=True)
