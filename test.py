import streamlit as st
import segno
from io import BytesIO
from PIL import Image
import time

# Page config
st.set_page_config(
    page_title="QR Magic ✨",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS moderne
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
.main {font-family: 'Poppins', sans-serif;}
.qr-card {background: rgba(255,255,255,0.95); backdrop-filter: blur(20px); border-radius: 24px; padding: 2rem; box-shadow: 0 25px 50px rgba(0,0,0,0.15);}
.fade-in {animation: fadeInUp 0.8s ease-out;}
@keyframes fadeInUp {from {opacity: 0; transform: translateY(30px);} to {opacity: 1; transform: translateY(0);}}
.gradient-btn {background: linear-gradient(45deg, #667eea, #764ba2); border-radius: 50px; padding: 12px 32px; font-weight: 600;}
.glass-input {border: 2px solid rgba(255,255,255,0.2); backdrop-filter: blur(20px); background: rgba(255,255,255,0.9); border-radius: 16px; padding: 16px;}
</style>
""", unsafe_allow_html=True)

st.title("🎨 **QR Code Magic Generator** ✨")
st.markdown("**Génère des QR codes parfaits - 100% Streamlit Cloud**")

# Layout
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 📝 **Votre contenu**")
    input_data = st.text_input(
        "Lien, texte ou message...",
        placeholder="https://google.com ou \"Bonjour !\"",
        key="input"
    )
    
    uploaded_file = st.file_uploader("📁 Fichier", type=['png','jpg','mp4','pdf'])

with col2:
    st.markdown("### 🎨 **Design**")
    size = st.slider("📏 Taille", 5, 15, 10)
    dark_color = st.color_picker("🖤 QR", "#000000")
    light_color = st.color_picker("⚪ Fond", "#FFFFFF")

# Génération
if st.button("✨ **CRÉER QR CODE** ✨", type="primary"):
    if input_data or uploaded_file:
        with st.spinner("🔮 Génération..."):
            # Contenu
            content = input_data or f"Fichier: {uploaded_file.name}"
            
            # QR avec segno (stable Streamlit Cloud)
            qr = segno.make(content, error='L')
            img = qr.to_pil(size=(size*30, size*30), 
                          dark=dark_color, light=light_color)
            
            # Download
            bio = BytesIO()
            img.save(bio, 'PNG')
            bio.seek(0)
            
            # Affichage
            st.markdown('<div class="qr-card fade-in" style="text-align:center;">', unsafe_allow_html=True)
            st.image(img, caption="✨ Votre QR Code", use_column_width=True)
            
            st.download_button(
                label="⬇️ TÉLÉCHARGER",
                data=bio.getvalue(),
                file_name="qr_code.png",
                mime="image/png"
            )
            st.success(f"✅ **QR prêt !** `{content[:30]}...`")
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.warning("⚠️ Saisissez un texte ou fichier")

# Boutons rapides
st.markdown("---")
col1, col2, col3 = st.columns(3)
if col1.button("🌐 Google"): st.session_state.input = "https://google.com"
if col2.button("📱 WhatsApp"): st.session_state.input = "https://wa.me/33600000000"
if col3.button("💳 Bitcoin"): st.session_state.input = "bitcoin:bc1qexample"

st.markdown("---")
st.markdown("*✨ QR Magic - Powered by Streamlit Cloud*")
