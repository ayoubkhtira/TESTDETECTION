# app.py
import streamlit as st
import qrcode
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import base64
import validators
import json
import time

# Configuration de la page - DOIT ÊTRE LA PREMIÈRE COMMANDE
st.set_page_config(
    page_title="QR Code Pro | Générateur Gratuit",
    page_icon="🔳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé moderne
st.markdown("""
<style>
/* Importation de police moderne */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

* {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Header stylé */
.main-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 2rem 1rem;
    border-radius: 20px;
    margin-bottom: 2rem;
    text-align: center;
    color: white;
    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
}

/* Cards modernes */
.qr-card {
    background: white;
    border-radius: 20px;
    padding: 2rem;
    box-shadow: 0 5px 20px rgba(0,0,0,0.08);
    margin-bottom: 1.5rem;
    border: 1px solid rgba(0,0,0,0.05);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.qr-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 15px 35px rgba(0,0,0,0.12);
}

/* Boutons stylés */
.stButton > button {
    border-radius: 12px;
    padding: 12px 24px;
    font-weight: 600;
    transition: all 0.3s ease;
    border: none;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 7px 20px rgba(0,0,0,0.15);
}

/* Sliders améliorés */
.stSlider > div > div > div {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

/* Input fields */
.stTextInput > div > div > input, 
.stTextArea > div > div > textarea {
    border-radius: 12px;
    border: 2px solid #e0e0e0;
    padding: 12px;
    font-size: 16px;
}

.stTextInput > div > div > input:focus, 
.stTextArea > div > div > textarea:focus {
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

/* Onglets personnalisés */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 12px 12px 0 0;
    padding: 12px 24px;
    font-weight: 500;
}

/* Animations */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

.fade-in {
    animation: fadeIn 0.6s ease-out;
}

/* Badges */
.badge {
    display: inline-block;
    padding: 4px 12px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    margin: 0 4px;
}

/* Amélioration des sélecteurs de couleur */
.stColorPicker > div > div > input {
    border-radius: 8px;
    border: 2px solid #e0e0e0;
}

/* Scrollbar personnalisée */
::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-track {
    background: #f1f1f1;
    border-radius: 4px;
}

::-webkit-scrollbar-thumb {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
}
</style>
""", unsafe_allow_html=True)

# Initialisation de session state
if 'generated_qr' not in st.session_state:
    st.session_state.generated_qr = None
if 'qr_data' not in st.session_state:
    st.session_state.qr_data = ""
if 'qr_config' not in st.session_state:
    st.session_state.qr_config = {}

# Fonctions utilitaires
def generate_qr_code(data, config):
    """Génère un QR code avec configuration"""
    try:
        qr = qrcode.QRCode(
            version=config.get('version', None),
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=config.get('box_size', 10),
            border=config.get('border', 4),
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(
            fill_color=config.get('fill_color', '#000000'),
            back_color=config.get('back_color', '#FFFFFF')
        )
        
        # Conversion PIL pour manipulation
        img = img.convert('RGBA')
        
        # Ajout de logo si spécifié
        if config.get('logo'):
            try:
                logo = Image.open(config['logo']).convert("RGBA")
                # Redimensionner le logo
                logo_size = config.get('logo_size', 15)  # pourcentage
                qr_size = img.size[0]
                logo_new_size = int(qr_size * logo_size / 100)
                logo = logo.resize((logo_new_size, logo_new_size))
                
                # Position au centre
                pos = ((qr_size - logo_new_size) // 2, 
                      (qr_size - logo_new_size) // 2)
                
                # Créer un mask pour transparence
                mask = logo.split()[3] if len(logo.split()) == 4 else None
                img.paste(logo, pos, mask)
            except Exception as e:
                st.warning(f"Impossible d'ajouter le logo: {e}")
        
        return img
    except Exception as e:
        st.error(f"Erreur lors de la génération du QR code: {e}")
        return None

def get_qr_download_link(img, filename="qr_code.png"):
    """Génère un lien de téléchargement pour l'image"""
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    href = f'<a href="data:image/png;base64,{img_str}" download="{filename}" style="text-decoration: none;">📥 Télécharger</a>'
    return href

def create_wifi_qr(ssid, password, security='WPA'):
    """Crée un QR code pour connexion WiFi"""
    security_map = {
        'WPA': 'WPA',
        'WEP': 'WEP',
        'None': 'nopass'
    }
    wifi_type = security_map.get(security, 'WPA')
    return f"WIFI:T:{wifi_type};S:{ssid};P:{password};;"

def create_vcard_qr(data):
    """Crée un QR code vCard"""
    vcard = "BEGIN:VCARD\nVERSION:3.0\n"
    vcard += f"FN:{data.get('name', '')}\n"
    vcard += f"TEL:{data.get('phone', '')}\n"
    vcard += f"EMAIL:{data.get('email', '')}\n"
    vcard += f"ORG:{data.get('company', '')}\n"
    vcard += f"TITLE:{data.get('title', '')}\n"
    vcard += f"ADR:{data.get('address', '')}\n"
    vcard += f"URL:{data.get('website', '')}\n"
    vcard += f"NOTE:{data.get('note', '')}\n"
    vcard += "END:VCARD"
    return vcard

# Header principal
st.markdown("""
<div class="main-header">
    <h1 style="margin:0; font-size: 2.8rem;">🔳 QR Code Pro</h1>
    <p style="margin:10px 0 0 0; font-size: 1.2rem; opacity: 0.9;">Générateur de QR codes gratuit & personnalisable</p>
    <div style="margin-top: 15px;">
        <span class="badge">Gratuit</span>
        <span class="badge">Sans limites</span>
        <span class="badge">100% Privé</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Layout principal
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### 📝 **Contenu du QR Code**")
    
    # Sélection du type de contenu
    content_type = st.selectbox(
        "Type de contenu",
        ["URL", "Texte", "Email", "WiFi", "Contact (vCard)", "SMS", "Téléphone", "Événement"],
        help="Sélectionnez le type de contenu à encoder"
    )
    
    # Champs dynamiques selon le type
    qr_data = ""
    
    if content_type == "URL":
        url = st.text_input("URL complète", placeholder="https://example.com", 
                           help="Commencez toujours par http:// ou https://")
        if url:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            qr_data = url
            
    elif content_type == "Texte":
        qr_data = st.text_area("Texte à encoder", height=150,
                              placeholder="Entrez votre texte ici...",
                              help="Tout texte peut être encodé dans un QR code")
        
    elif content_type == "Email":
        col_email1, col_email2 = st.columns(2)
        with col_email1:
            email = st.text_input("Adresse email", placeholder="contact@exemple.com")
        with col_email2:
            subject = st.text_input("Sujet", placeholder="Sujet du message")
        body = st.text_area("Message", placeholder="Corps du message")
        
        if email:
            qr_data = f"mailto:{email}"
            if subject or body:
                qr_data += "?"
                params = []
                if subject:
                    params.append(f"subject={subject}")
                if body:
                    params.append(f"body={body}")
                qr_data += "&".join(params)
                
    elif content_type == "WiFi":
        col_wifi1, col_wifi2 = st.columns(2)
        with col_wifi1:
            ssid = st.text_input("Nom du réseau (SSID)", placeholder="Nom WiFi")
        with col_wifi2:
            password = st.text_input("Mot de passe", type="password")
        security = st.selectbox("Type de sécurité", ["WPA/WPA2", "WEP", "Aucun"])
        
        if ssid and password:
            qr_data = create_wifi_qr(ssid, password, security)
            
    elif content_type == "Contact (vCard)":
        col_vcard1, col_vcard2 = st.columns(2)
        with col_vcard1:
            name = st.text_input("Nom complet")
            phone = st.text_input("Téléphone")
            email_vcard = st.text_input("Email")
        with col_vcard2:
            company = st.text_input("Entreprise")
            title = st.text_input("Poste")
            website = st.text_input("Site web")
        
        vcard_data = {
            'name': name,
            'phone': phone,
            'email': email_vcard,
            'company': company,
            'title': title,
            'website': website
        }
        qr_data = create_vcard_qr(vcard_data)
        
    elif content_type == "SMS":
        col_sms1, col_sms2 = st.columns(2)
        with col_sms1:
            sms_number = st.text_input("Numéro de téléphone", placeholder="+33612345678")
        with col_sms2:
            sms_body = st.text_input("Message SMS")
        
        if sms_number:
            qr_data = f"SMSTO:{sms_number}"
            if sms_body:
                qr_data += f":{sms_body}"
                
    elif content_type == "Téléphone":
        phone = st.text_input("Numéro de téléphone", placeholder="+33612345678")
        if phone:
            qr_data = f"tel:{phone}"
            
    elif content_type == "Événement":
        col_event1, col_event2 = st.columns(2)
        with col_event1:
            event_title = st.text_input("Titre de l'événement")
            event_date = st.date_input("Date")
            event_time = st.time_input("Heure")
        with col_event2:
            event_location = st.text_input("Lieu")
            event_description = st.text_area("Description")
        
        if event_title:
            qr_data = f"BEGIN:VEVENT\nSUMMARY:{event_title}\n"
            if event_date:
                qr_data += f"DTSTART:{event_date}"
                if event_time:
                    qr_data += f"T{event_time}"
            if event_location:
                qr_data += f"\nLOCATION:{event_location}"
            if event_description:
                qr_data += f"\nDESCRIPTION:{event_description}"
            qr_data += "\nEND:VEVENT"

with col2:
    st.markdown("### 🎨 **Personnalisation**")
    
    # Options de personnalisation
    with st.expander("📏 **Dimensions**", expanded=True):
        col_size1, col_size2 = st.columns(2)
        with col_size1:
            box_size = st.slider("Taille des modules", 5, 30, 10, 
                                help="Taille des points du QR code")
        with col_size2:
            border = st.slider("Bordure", 1, 10, 4, 
                              help="Espace blanc autour du QR code")
    
    with st.expander("🎨 **Couleurs**", expanded=True):
        col_color1, col_color2 = st.columns(2)
        with col_color1:
            fill_color = st.color_picker("Couleur des modules", "#000000")
        with col_color2:
            back_color = st.color_picker("Couleur de fond", "#FFFFFF")
    
    with st.expander("🖼️ **Logo personnalisé**"):
        logo_file = st.file_uploader("Ajouter un logo", type=['png', 'jpg', 'jpeg'],
                                    help="Le logo sera placé au centre du QR code")
        if logo_file:
            logo_size = st.slider("Taille du logo (%)", 10, 40, 15)
    
    with st.expander("⚙️ **Paramètres avancés**"):
        version = st.selectbox("Version QR", 
                              ["Auto"] + [str(i) for i in range(1, 41)],
                              help="Version 1-40 (plus grand = plus de données)")
        error_correction = st.selectbox(
            "Correction d'erreurs",
            ["L (7%)", "M (15%)", "Q (25%)", "H (30%)"],
            help="Plus la correction est élevée, plus le QR code est robuste"
        )
        
        # Mapping correction d'erreurs
        error_map = {
            "L (7%)": qrcode.constants.ERROR_CORRECT_L,
            "M (15%)": qrcode.constants.ERROR_CORRECT_M,
            "Q (25%)": qrcode.constants.ERROR_CORRECT_Q,
            "H (30%)": qrcode.constants.ERROR_CORRECT_H
        }

# Bouton de génération principal
generate_col1, generate_col2, generate_col3 = st.columns([1, 2, 1])
with generate_col2:
    generate_btn = st.button("🚀 **GÉNÉRER LE QR CODE**", 
                            type="primary", 
                            use_container_width=True,
                            disabled=not qr_data)

# Génération du QR code
if generate_btn and qr_data:
    with st.spinner("🔄 **Génération en cours...**"):
        # Préparation de la configuration
        config = {
            'box_size': box_size,
            'border': border,
            'fill_color': fill_color,
            'back_color': back_color,
            'logo': logo_file,
            'logo_size': logo_size if logo_file else 0,
            'version': None if version == "Auto" else int(version),
            'error_correction': error_map.get(error_correction, qrcode.constants.ERROR_CORRECT_H)
        }
        
        # Sauvegarde dans session state
        st.session_state.qr_data = qr_data
        st.session_state.qr_config = config
        
        # Génération
        qr_image = generate_qr_code(qr_data, config)
        
        if qr_image:
            st.session_state.generated_qr = qr_image
            
            # Animation de succès
            st.success("✅ **QR code généré avec succès !**")
            st.balloons()

# Affichage du QR code généré
if st.session_state.generated_qr:
    st.markdown("---")
    st.markdown("### 📱 **Votre QR Code**")
    
    # Affichage dans une card
    with st.container():
        st.markdown('<div class="qr-card fade-in">', unsafe_allow_html=True)
        
        col_display1, col_display2 = st.columns([2, 1])
        
        with col_display1:
            # Afficher l'image
            st.image(st.session_state.generated_qr, 
                    use_column_width=True,
                    caption="Votre QR code personnalisé")
        
        with col_display2:
            st.markdown("#### 📊 **Informations**")
            st.markdown(f"**Type:** {content_type}")
            st.markdown(f"**Taille:** {box_size}px/module")
            st.markdown(f"**Couleur:** {fill_color}")
            
            # Téléchargement
            st.markdown("---")
            st.markdown("#### 💾 **Télécharger**")
            
            # Formats disponibles
            format_col1, format_col2 = st.columns(2)
            with format_col1:
                if st.button("PNG", use_container_width=True):
                    buffered = BytesIO()
                    st.session_state.generated_qr.save(buffered, format="PNG")
                    st.download_button(
                        label="📥 Télécharger PNG",
                        data=buffered.getvalue(),
                        file_name="qr_code.png",
                        mime="image/png",
                        use_container_width=True
                    )
            
            with format_col2:
                if st.button("JPG", use_container_width=True):
                    buffered = BytesIO()
                    rgb_image = st.session_state.generated_qr.convert('RGB')
                    rgb_image.save(buffered, format="JPEG", quality=95)
                    st.download_button(
                        label="📥 Télécharger JPG",
                        data=buffered.getvalue(),
                        file_name="qr_code.jpg",
                        mime="image/jpeg",
                        use_container_width=True
                    )
            
            # Taille recommandée pour impression
            st.info(f"**💡 Conseil:** Taille recommandée pour impression: **{box_size * 3}mm**")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Test du QR code
        st.markdown("### 🔍 **Tester votre QR code**")
        test_col1, test_col2, test_col3 = st.columns(3)
        with test_col1:
            if st.button("📱 Scanner avec téléphone", use_container_width=True):
                st.info("Utilisez l'appareil photo de votre téléphone pour scanner ce QR code")
        with test_col2:
            if st.button("🔄 Regénérer", use_container_width=True):
                st.rerun()
        with test_col3:
            if st.button("🗑️ Réinitialiser", use_container_width=True):
                st.session_state.generated_qr = None
                st.session_state.qr_data = ""
                st.rerun()

# Section des QR codes rapides
st.markdown("---")
st.markdown("### ⚡ **QR Codes Rapides**")

quick_cols = st.columns(4)
with quick_cols[0]:
    if st.button("🌐 Google", use_container_width=True):
        st.session_state.qr_data = "https://www.google.com"
        st.rerun()
with quick_cols[1]:
    if st.button("📱 WhatsApp", use_container_width=True):
        st.session_state.qr_data = "https://wa.me/33600000000"
        st.rerun()
with quick_cols[2]:
    if st.button("📧 Gmail", use_container_width=True):
        st.session_state.qr_data = "https://mail.google.com"
        st.rerun()
with quick_cols[3]:
    if st.button("📍 Maps", use_container_width=True):
        st.session_state.qr_data = "https://maps.google.com"
        st.rerun()

# Section d'utilisation
with st.expander("📚 **Guide d'utilisation**", expanded=False):
    st.markdown("""
    ### Comment utiliser QR Code Pro ?
    
    1. **Choisissez le type de contenu** que vous souhaitez encoder
    2. **Remplissez les champs** nécessaires (URL, texte, etc.)
    3. **Personnalisez l'apparence** du QR code (couleurs, taille, logo)
    4. **Générez et téléchargez** votre QR code
    
    ### 💡 **Conseils pratiques**
    
    | Utilisation | Paramètres recommandés |
    |-------------|------------------------|
    | Impression | Taille module ≥ 10, Correction H |
    | Petit format | Logo ≤ 15% de la taille |
    | Usage extérieur | Couleurs contrastées |
    | Données longues | Version Auto |
    
    ### 🛡️ **Sécurité et confidentialité**
    - Vos données ne sont **jamais stockées** sur nos serveurs
    - Toute la génération se fait **localement** dans votre navigateur
    - Aucune limitation d'utilisation
    """)

# Pied de page
st.markdown("---")
footer_col1, footer_col2, footer_col3 = st.columns([1, 2, 1])
with footer_col2:
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 2rem 0;">
        <p style="margin: 0; font-size: 0.9rem;">
            <strong>QR Code Pro</strong> • Générateur gratuit de QR codes • 
            <a href="https://github.com/your-repo" target="_blank" style="color: #667eea; text-decoration: none;">
                Code source
            </a>
        </p>
        <p style="margin: 10px 0 0 0; font-size: 0.8rem;">
            © 2024 • Version 1.0 • Aucune donnée personnelle collectée
        </p>
    </div>
    """, unsafe_allow_html=True)

# Sidebar avec informations supplémentaires
with st.sidebar:
    st.markdown("### ℹ️ **À propos**")
    st.markdown("""
    **QR Code Pro** est un générateur de QR codes :
    
    ✓ **100% gratuit** - Pas de limitations
    ✓ **Aucun enregistrement** - Vos données restent privées
    ✓ **Fonctionne hors ligne** - Après chargement initial
    ✓ **Multi-formats** - PNG, JPG
    ✓ **Personnalisation avancée** - Couleurs, logos, etc.
    """)
    
    st.markdown("---")
    st.markdown("### 📊 **Statistiques**")
    
    if st.session_state.generated_qr:
        qr_size = st.session_state.generated_qr.size
        data_length = len(st.session_state.qr_data)
        
        st.metric("📏 Taille du QR", f"{qr_size[0]}×{qr_size[1]} px")
        st.metric("📊 Données encodées", f"{data_length} caractères")
        st.metric("🎨 Couleur principale", st.session_state.qr_config.get('fill_color', '#000000'))
    
    st.markdown("---")
    st.markdown("### 🌐 **Partager**")
    
    if st.session_state.generated_qr:
        buffered = BytesIO()
        st.session_state.generated_qr.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        html_code = f'<img src="data:image/png;base64,{img_str}" width="200" alt="QR Code">'
        
        st.code(html_code, language='html')
        st.caption("Code HTML pour intégration")
