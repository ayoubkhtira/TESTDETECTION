import streamlit as st
import segno
from io import BytesIO
from PIL import Image
import base64
import time

# Configuration de la page - DOIT ÊTRE LA PREMIÈRE COMMANDE
st.set_page_config(
    page_title="QR Magic ✨",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS moderne amélioré
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
.main {font-family: 'Poppins', sans-serif;}
.qr-card {
    background: rgba(255,255,255,0.95);
    backdrop-filter: blur(20px);
    border-radius: 24px;
    padding: 2rem;
    box-shadow: 0 25px 50px rgba(0,0,0,0.15);
    margin: 1rem 0;
    transition: transform 0.3s ease;
}
.qr-card:hover {
    transform: translateY(-5px);
}
.fade-in {animation: fadeInUp 0.8s ease-out;}
@keyframes fadeInUp {
    from {opacity: 0; transform: translateY(30px);}
    to {opacity: 1; transform: translateY(0);}
}
.gradient-btn {
    background: linear-gradient(45deg, #667eea, #764ba2);
    border-radius: 50px;
    padding: 12px 32px;
    font-weight: 600;
    border: none;
    color: white;
    cursor: pointer;
    transition: all 0.3s ease;
}
.gradient-btn:hover {
    transform: scale(1.05);
    box-shadow: 0 10px 20px rgba(0,0,0,0.2);
}
.glass-input {
    border: 2px solid rgba(255,255,255,0.2);
    backdrop-filter: blur(20px);
    background: rgba(255,255,255,0.9);
    border-radius: 16px;
    padding: 16px;
}
.stButton > button {
    width: 100%;
}
.download-btn {
    background: linear-gradient(45deg, #4CAF50, #2E7D32);
    color: white;
    border-radius: 25px;
    padding: 12px 24px;
    border: none;
    font-weight: 600;
    margin-top: 1rem;
}
.quick-btn {
    margin: 0.2rem;
    border-radius: 20px;
}
</style>
""", unsafe_allow_html=True)

# Titre avec effet
st.markdown("<h1 style='text-align: center; color: linear-gradient(45deg, #667eea, #764ba2);'>🎨 <span style='background: linear-gradient(45deg, #667eea, #764ba2); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>QR Code Magic Generator</span> ✨</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666;'>Générez des QR codes personnalisés en quelques secondes - 100% compatible Streamlit Cloud</p>", unsafe_allow_html=True)

# Sidebar pour paramètres avancés
with st.sidebar:
    st.markdown("### ⚙️ Paramètres avancés")
    
    # Niveau de correction d'erreur
    error_correction = st.selectbox(
        "Niveau de correction d'erreur",
        ["L (7%)", "M (15%)", "Q (25%)", "H (30%)"],
        help="Niveau de tolérance aux erreurs/dégâts"
    )
    
    # Mapping des niveaux
    error_map = {
        "L (7%)": "L",
        "M (15%)": "M",
        "Q (25%)": "Q",
        "H (30%)": "H"
    }
    
    # Format d'image
    image_format = st.selectbox(
        "Format d'image",
        ["PNG", "SVG", "PDF"],
        help="Format de téléchargement"
    )
    
    # Ajouter un logo optionnel
    logo_file = st.file_uploader(
        "🖼️ Ajouter un logo (optionnel)",
        type=['png', 'jpg', 'jpeg'],
        help="Logo à placer au centre du QR code"
    )
    
    if logo_file:
        logo_size = st.slider("Taille du logo", 10, 50, 25, help="Taille en pourcentage du QR code")

# Layout principal
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 📝 **Votre contenu**")
    
    # Type de contenu
    content_type = st.radio(
        "Type de contenu",
        ["URL", "Texte", "Email", "Téléphone", "Wifi", "VCard"],
        horizontal=True
    )
    
    # Champs selon le type
    if content_type == "URL":
        input_data = st.text_input(
            "URL complète",
            placeholder="https://exemple.com",
            key="input_url"
        )
    elif content_type == "Email":
        email = st.text_input("Adresse email", placeholder="contact@exemple.com")
        subject = st.text_input("Sujet (optionnel)", placeholder="Bonjour !")
        body = st.text_area("Message (optionnel)")
        input_data = f"mailto:{email}"
        if subject:
            input_data += f"?subject={subject}"
        if body:
            input_data += f"&body={body}" if subject else f"?body={body}"
    elif content_type == "Téléphone":
        phone = st.text_input("Numéro de téléphone", placeholder="+33612345678")
        input_data = f"tel:{phone}"
    elif content_type == "Wifi":
        ssid = st.text_input("Nom du réseau (SSID)")
        password = st.text_input("Mot de passe", type="password")
        encryption = st.selectbox("Cryptage", ["WPA", "WEP", "Aucun"])
        input_data = f"WIFI:T:{encryption};S:{ssid};P:{password};;"
    elif content_type == "VCard":
        name = st.text_input("Nom complet")
        tel = st.text_input("Téléphone")
        email_vcard = st.text_input("Email")
        input_data = f"BEGIN:VCARD\nVERSION:3.0\nFN:{name}\nTEL:{tel}\nEMAIL:{email_vcard}\nEND:VCARD"
    else:  # Texte
        input_data = st.text_area(
            "Votre texte",
            placeholder="Entrez votre texte ici...",
            height=100,
            key="input_text"
        )
    
    # Téléchargement de fichier
    uploaded_file = st.file_uploader(
        "📁 **OU télécharger un fichier**",
        type=['png', 'jpg', 'pdf', 'txt', 'docx', 'xlsx'],
        help="Le QR code pointera vers le fichier téléchargé"
    )

with col2:
    st.markdown("### 🎨 **Design**")
    
    # Taille
    size = st.slider("📏 Taille du QR code", 5, 20, 10, help="Multiplicateur de taille")
    
    # Couleurs
    col_color1, col_color2 = st.columns(2)
    with col_color1:
        dark_color = st.color_picker("🖤 Couleur du QR", "#000000")
    with col_color2:
        light_color = st.color_picker("⚪ Couleur de fond", "#FFFFFF")
    
    # Style des modules
    module_style = st.selectbox(
        "Style des modules",
        ["Carrés", "Ronds", "Arrondis"],
        help="Forme des points du QR code"
    )

# Bouton de génération
if st.button("✨ **GÉNÉRER LE QR CODE** ✨", type="primary", use_container_width=True):
    if input_data or uploaded_file:
        with st.spinner("🔮 Génération en cours..."):
            # Contenu
            content = input_data
            if uploaded_file:
                # Pour un vrai projet, vous devriez stocker le fichier et générer une URL
                content = f"Fichier: {uploaded_file.name} - {uploaded_file.type}"
            
            # Création du QR code
            qr = segno.make(content, error=error_map[error_correction])
            
            # Conversion en image PIL
            img = qr.to_pil(
                size=(size * 30, size * 30),
                dark=dark_color,
                light=light_color,
                quiet_zone="#FFFFFF"
            )
            
            # Ajout du logo si fourni
            if logo_file:
                try:
                    logo = Image.open(logo_file)
                    # Redimensionner le logo
                    qr_width, qr_height = img.size
                    logo_size_px = int(qr_width * (logo_size / 100))
                    logo = logo.resize((logo_size_px, logo_size_px))
                    
                    # Positionner au centre
                    position = ((qr_width - logo_size_px) // 2, (qr_height - logo_size_px) // 2)
                    
                    # Créer une image avec transparence
                    img = img.convert("RGBA")
                    logo = logo.convert("RGBA")
                    img.paste(logo, position, logo)
                except Exception as e:
                    st.warning(f"Impossible d'ajouter le logo : {e}")
            
            # Préparation du téléchargement
            bio = BytesIO()
            img.save(bio, format='PNG')
            bio.seek(0)
            
            # Afficher le QR code
            st.markdown('<div class="qr-card fade-in">', unsafe_allow_html=True)
            st.markdown("### ✅ **Votre QR Code est prêt !**")
            
            col_img, col_info = st.columns([2, 1])
            
            with col_img:
                st.image(img, use_column_width=True)
            
            with col_info:
                st.markdown("**📋 Informations:**")
                st.code(content[:100] + "..." if len(content) > 100 else content)
                st.markdown(f"**📏 Taille:** {size}")
                st.markdown(f"**🎨 Couleurs:** {dark_color} / {light_color}")
                st.markdown(f"**🛡️ Correction:** {error_correction}")
            
            # Bouton de téléchargement
            st.download_button(
                label=f"⬇️ TÉLÉCHARGER ({image_format})",
                data=bio.getvalue(),
                file_name=f"qr_code_magic.{image_format.lower()}",
                mime=f"image/{image_format.lower()}" if image_format != "PDF" else "application/pdf",
                key="download_qr",
                use_container_width=True
            )
            
            # Code HTML pour intégration
            with st.expander("📋 Code d'intégration HTML"):
                img_base64 = base64.b64encode(bio.getvalue()).decode()
                html_code = f'<img src="data:image/png;base64,{img_base64}" alt="QR Code" width="200">'
                st.code(html_code, language='html')
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Effet de succès
            st.balloons()
    else:
        st.warning("⚠️ Veuillez saisir du texte ou télécharger un fichier")

# Boutons rapides
st.markdown("---")
st.markdown("### 🔗 **Liens rapides**")

col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("🌐 Google", use_container_width=True, key="google"):
        st.session_state.input_url = "https://google.com"
        st.rerun()
with col2:
    if st.button("📱 WhatsApp", use_container_width=True, key="whatsapp"):
        st.session_state.input_url = "https://wa.me/33600000000"
        st.rerun()
with col3:
    if st.button("📧 Email", use_container_width=True, key="email"):
        st.session_state.input_text = "mailto:contact@exemple.com?subject=Bonjour&body=Message"
        st.rerun()
with col4:
    if st.button("📍 Google Maps", use_container_width=True, key="maps"):
        st.session_state.input_url = "https://maps.google.com"
        st.rerun()

# Section d'aide
with st.expander("❓ **Comment ça marche ?**"):
    st.markdown("""
    ### Guide d'utilisation:
    1. **Saisissez votre contenu** : URL, texte, ou téléchargez un fichier
    2. **Personnalisez l'apparence** : Couleurs, taille, style
    3. **Ajoutez un logo** (optionnel) : Téléchargez votre logo dans la sidebar
    4. **Générez et téléchargez** votre QR code
    
    ### Conseils:
    - Utilisez la correction d'erreur **H (30%)** pour les QR codes avec logo
    - Les QR codes trop denses (beaucoup de données) nécessitent une plus grande taille
    - Testez toujours votre QR code avant de l'imprimer
    
    ### Formats supportés:
    - **URLs** : Sites web, liens profonds
    - **Contacts** : vCard pour ajouter des contacts
    - **WiFi** : Partage de réseau WiFi
    - **Téléphone** : Appels directs
    - **Email** : Rédaction d'emails
    """)

# Pied de page
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; padding: 1rem;'>
        <p>✨ <strong>QR Magic Generator</strong> - Créé avec ❤️ et Streamlit</p>
        <p style='font-size: 0.8rem;'>Gratuit • Sans publicité • 100% Open Source</p>
    </div>
    """,
    unsafe_allow_html=True
)
