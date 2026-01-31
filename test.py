import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.express as px
import time

st.set_page_config(page_title="VisionGuard Lite", layout="wide")

st.title("🤖 VisionGuard AI Lite")
st.write("Version simplifiée - Fonctionnalités de base")

# Simulation de données
if st.button("Simuler une alerte"):
    st.success("Alerte simulée envoyée !")
    
# Interface de démonstration
tab1, tab2 = st.tabs(["📊 Dashboard", "📋 Historique"])

with tab1:
    st.subheader("Statistiques simulées")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Personnes détectées", "12", "+3")
    with col2:
        st.metric("Alertes envoyées", "5", "+1")
    with col3:
        st.metric("Taux de détection", "98%", "-2%")

with tab2:
    st.subheader("Historique des événements")
    data = pd.DataFrame({
        "Heure": [datetime.now().strftime("%H:%M:%S") for _ in range(10)],
        "Événement": ["Détection téléphone", "Détection personne", "Alerte envoyée"] * 3 + ["Système OK"],
        "Statut": ["✅", "⚠️", "🚨", "✅", "⚠️", "🚨", "✅", "⚠️", "🚨", "✅"]
    })
    st.dataframe(data)
