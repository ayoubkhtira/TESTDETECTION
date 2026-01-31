# app.py (pour Streamlit Cloud)
import streamlit as st
import qrcode
from io import BytesIO, BytesIO
from PIL import Image
import base64
import io

# CSS moderne avec animations
st.markdown("""
<style>
    .main {background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);}
    .qr-card {background: rgba(255,255,255,0.1); backdrop-filter: blur(20px);}
    @keyframes fadeIn {from {opacity: 0; transform: translateY(30px);} to {opacity: 1; transform: translateY(0);}}
    .fade-in {animation: fadeIn 0.8s ease-out;}
</style>
""", unsafe_allow_html=True)

st.title("🎨 QR Code Magic")
st.markdown("---")

# Sidebar pour upload
with st.sidebar:
    st.header("📁 Upload")
    uploaded_file = st.file_uploader("Image/Vidéo", type=['png','jpg','jpeg','mp4','avi'])

# Input principal
col1, col2 = st.columns([3,1])
with col1:
    input_data = st.text_input("👇 Lien/Texte", placeholder="https://google.com ou votre texte...")
with col2:
    generate = st.button("✨ Générer", type="primary")

# Animation particules
if st.button("🎊 Particules !"):
    st.balloons()

# Logique QR
if generate and input_data:
    with st.spinner("🔮 Génération magique..."):
        # Créer QR
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(input_data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Buffer pour download
        bio = BytesIO()
        img.save(bio, format='PNG')
        bio.seek(0)
        
        # Affichage
        st.markdown('<div class="qr-card fade-in" style="padding:2rem;border-radius:20px;text-align:center;">', unsafe_allow_html=True)
        st.image(img, caption="Votre QR Code ✨", use_column_width=True)
        
        # Download
        st.download_button(
            label="⬇️ Télécharger",
            data=bio.getvalue(),
            file_name="qr_magic.png",
            mime="image/png"
        )
        st.markdown('</div>', unsafe_allow_html=True)

# Upload handling
elif uploaded_file:
    input_data = f"Fichier: {uploaded_file.name}"
    st.success(f"📁 {uploaded_file.name} uploadé !")
    st.info("Ajoutez du texte pour générer le QR")

# Footer
st.markdown("---")
st.markdown("*✨ QR Code Generator - Powered by Streamlit Cloud*")
