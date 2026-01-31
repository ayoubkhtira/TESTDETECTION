import streamlit as st
import qrcode
from io import BytesIO
from PIL import Image
import base64
import time

# Page config
st.set_page_config(
    page_title="QR Magic ✨",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS moderne avec animations
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        font-family: 'Poppins', sans-serif;
    }
    
    .qr-card {
        background: rgba(255,255,255,0.95);
        backdrop-filter: blur(20px);
        border-radius: 24px;
        padding: 2rem;
        box-shadow: 0 25px 50px rgba(0,0,0,0.15);
        border: 1px solid rgba(255,255,255,0.2);
    }
    
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .fade-in { animation: fadeInUp 0.8s ease-out; }
    
    .gradient-btn {
        background: linear-gradient(45deg, #667eea, #764ba2);
        border: none;
        border-radius: 50px;
        padding: 12px 32px;
        font-weight: 600;
        font-size: 16px;
        transition: all 0.3s ease;
        box-shadow: 0 10px 30px rgba(102,126,234,0.4);
    }
    
    .gradient-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 20px 40px rgba(102,126,234,0.6);
    }
    
    .glass-input {
        border: 2px solid rgba(255,255,255,0.2);
        backdrop-filter: blur(20px);
        background: rgba(255,255,255,0.9);
        border-radius: 16px;
        padding: 16px;
        transition: all 0.3s ease;
    }
    
    .glass-input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 4px rgba(102,126,234,0.1);
        transform: scale(1.02);
    }
</style>
""", unsafe_allow_html=True)

# Header
st.title("🎨 **QR Code Magic Generator** ✨")
st.markdown("**Générez des QR codes stylés en 1 clic !** 📱💻")

# Colonnes principales
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 📝 **Saisir votre contenu**")
    
    # Input principal avec animation
    input_data = st.text_input(
        "Lien, texte ou message...",
        placeholder="https://google.com ou \"Bonjour le monde !\"",
        key="main_input",
        help="Entrez n'importe quel texte ou URL"
    )
    
    # Upload fichier
    uploaded_file = st.file_uploader(
        "📁 Ou uploader un fichier",
        type=['png', 'jpg', 'jpeg', 'mp4', 'pdf', 'txt'],
        help="Image, vidéo, document..."
    )
    
    if uploaded_file:
        input_data = f"Fichier: {uploaded_file.name}"
        st.success(f"✅ **{uploaded_file.name}** uploadé !")

with col2:
    st.markdown("### 🎨 **Options**")
    
    # Couleurs personnalisées
    col1c, col2c = st.columns(2)
    with col1c:
        qr_color = st.color_picker("🎨 Couleur QR", "#000000")
    with col2c:
        bg_color = st.color_picker("🌈 Fond", "#FFFFFF")
    
    # Taille
    size = st.slider("📏 Taille QR", 1, 20, 10)

# Bouton génération
if st.button("✨ **GÉNÉRER QR CODE** ✨", type="primary", key="generate", 
             help="Cliquez pour créer votre QR code magique !"):
    
    if input_data:
        with st.spinner("🔮 **Génération magique en cours...**"):
            time.sleep(0.5)  # Animation
            
            # Créer QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=size * 5,
                border=4,
            )
            qr.add_data(input_data)
            qr.make(fit=True)
            
            # Générer image
            img = qr.make_image(fill_color=qr_color, back_color=bg_color)
            
            # Buffer pour download
            bio = BytesIO()
            img.save(bio, 'PNG')
            bio.seek(0)
            
            # Affichage avec animation
            st.markdown("""
            <div class="qr-card fade-in" style="text-align: center; max-width: 400px; margin: 0 auto;">
            """, unsafe_allow_html=True)
            
            st.image(img, caption="✨ **Votre QR Code est prêt !**", use_column_width=True)
            
            # Download
            st.download_button(
                label="⬇️ **TÉLÉCHARGER QR**",
                data=bio.getvalue(),
                file_name=f"qr_magic_{int(time.time())}.png",
                mime="image/png",
                key="download"
            )
            
            # Info
            st.info(f"**Texte encodé :** `{input_data[:50]}...`")
            st.success("✅ **QR Code généré avec succès !**")
            
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.warning("⚠️ **Veuillez saisir un texte ou uploader un fichier**")

# Exemples
with st.expander("📚 **Exemples rapides**"):
    col_ex1, col_ex2, col_ex3 = st.columns(3)
    
    with col_ex1:
        if st.button("🏠 Google", key="ex1"):
            st.session_state.main_input = "https://google.com"
    with col_ex2:
        if st.button("📱 WhatsApp", key="ex2"):
            st.session_state.main_input = "https://wa.me/33612345678"
    with col_ex3:
        if st.button("💳 Bitcoin", key="ex3"):
            st.session_state.main_input = "bitcoin:bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh"

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: rgba(255,255,255,0.8);'>
        ✨ **QR Code Magic** - Powered by Streamlit Cloud 
        <br>📱 Compatible mobile • 🚀 Déployé en 30s
    </div>
    """, 
    unsafe_allow_html=True
)
