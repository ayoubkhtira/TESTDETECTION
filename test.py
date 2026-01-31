import reflex as rx
import qrcode
from io import BytesIO
from PIL import Image
from typing import Optional
import base64

class QRGeneratorState(rx.State):
    input_data: str = ""
    qr_image: Optional[str] = None  # Base64 image
    file_content: Optional[str] = ""  # Base64 uploaded file
    theme: str = "dark"
    is_generating: bool = False

    def generate_qr(self):
        if not self.input_data.strip():
            return
        
        self.is_generating = True
        
        # Générer QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(self.input_data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convertir en base64
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        self.qr_image = f"data:image/png;base64,{img_str}"
        self.is_generating = False

    def handle_upload(self, files: list):
        if files:
            file = files[0]
            self.file_content = file.content.decode()
            self.input_data = f"Uploaded: {file.name}"
            self.generate_qr()

    def copy_to_clipboard(self):
        rx.window.copy(self.input_data)

    def toggle_theme(self):
        self.theme = "light" if self.theme == "dark" else "dark"

def particle_bg():
    return rx.vstack(
        rx.div(
            rx.div(
                "✨",
                class_name="particle",
                style={
                    "animation": "float 6s ease-in-out infinite",
                    "position": "absolute",
                    "font_size": "20px",
                    "opacity": "0.7"
                }
            ),
            rx.div(
                "✨",
                class_name="particle",
                style={
                    "animation": "float 8s ease-in-out infinite reverse",
                    "position": "absolute",
                    "font_size": "16px",
                    "opacity": "0.5",
                    "animation_delay": "2s"
                }
            ),
        ),
        class_name="particles",
        position="fixed",
        top="0",
        left="0",
        width="100%",
        height="100%",
        z_index="0",
        pointer_events="none"
    )

def qr_generator():
    return rx.fragment(
        particle_bg(),
        rx.center(
            rx.vstack(
                # Header animé
                rx.heading(
                    "🎨 QR Code Magic",
                    class_name="hero-title",
                    font_size="3rem",
                    margin_bottom="2rem"
                ),
                
                # Toggle thème
                rx.button(
                    "🌙" if state.theme == "dark" else "☀️",
                    on_click=state.toggle_theme,
                    size="3",
                    variant="outline",
                    class_name="theme-toggle"
                ),
                
                # Zone d'input principale
                rx.paper(
                    rx.vstack(
                        rx.input(
                            placeholder="Saisir un lien, texte ou URL...",
                            value=state.input_data,
                            on_change=state.set_input_data,
                            class_name="modern-input",
                            size="3"
                        ),
                        rx.button(
                            "✨ Générer QR",
                            on_click=state.generate_qr,
                            is_loading=state.is_generating,
                            class_name="generate-btn",
                            size="3",
                            color_scheme="gradient"
                        ),
                        rx.button(
                            "📋 Copier",
                            on_click=state.copy_to_clipboard,
                            class_name="copy-btn",
                            size="2",
                            variant="soft"
                        )
                    ),
                    class_name="input-container",
                    padding="2rem",
                    border_radius="2rem",
                    shadow="2xl"
                ),
                
                # Upload zone
                rx.paper(
                    rx.upload(
                        rx.button(
                            "📁 Upload Image/Vidéo",
                            class_name="upload-btn",
                            size="2"
                        ),
                        on_upload=state.handle_upload,
                        multiple=False,
                        accept="image/*,video/*"
                    ),
                    class_name="upload-container",
                    padding="1.5rem",
                    border_radius="1.5rem"
                ),
                
                # QR Code résultat
                rx.cond(
                    state.qr_image,
                    rx.paper(
                        rx.image(
                            src=state.qr_image,
                            width="300px",
                            height="300px",
                            border_radius="1rem",
                            box_shadow="0 20px 40px rgba(0,0,0,0.3)",
                            class_name="qr-image"
                        ),
                        rx.button(
                            "⬇️ Télécharger",
                            on_click=lambda: rx.download(
                                data=state.qr_image,
                                filename="mon_qr.png"
                            ),
                            class_name="download-btn",
                            size="2"
                        ),
                        class_name="qr-container",
                        text_align="center",
                        padding="3rem"
                    )
                ),
                
                # Footer
                rx.text(
                    "✨ Créez des QR codes magiques en 1 clic !",
                    class_name="footer-text",
                    size="1",
                    opacity="0.8"
                )
            ),
            class_name="main-content",
            padding="2rem",
            max_width="600px"
        ),
        position="relative",
        height="100vh",
        z_index="1"
    )

# Styles CSS personnalisés
def custom_style():
    return """
    @keyframes float {
        0%, 100% { transform: translateY(0px) rotate(0deg); }
        50% { transform: translateY(-20px) rotate(180deg); }
    }
    
    .particles {
        overflow: hidden;
    }
    
    .hero-title {
        background: linear-gradient(45deg, #ff6b6b, #4ecdc4, #45b7d1, #f9ca24);
        background-size: 400% 400%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: gradientShift 3s ease infinite;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .modern-input {
        border: 2px solid rgba(255,255,255,0.2) !important;
        backdrop-filter: blur(20px);
        transition: all 0.3s ease;
        background: rgba(255,255,255,0.1) !important;
    }
    
    .modern-input:focus {
        border-color: #4ecdc4 !important;
        box-shadow: 0 0 20px rgba(78, 205, 196, 0.5);
        transform: scale(1.02);
    }
    
    .generate-btn {
        background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
        border: none !important;
        border-radius: 50px !important;
        font-weight: bold !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
    }
    
    .generate-btn:hover {
        transform: translateY(-3px);
        box-shadow: 0 20px 40px rgba(102, 126, 234, 0.6);
    }
    
    .qr-image {
        animation: qrAppear 0.8s cubic-bezier(0.25, 0.46, 0.45, 0.94);
    }
    
    @keyframes qrAppear {
        0% { opacity: 0; transform: scale(0.3) rotate(-10deg); }
        100% { opacity: 1; transform: scale(1) rotate(0deg); }
    }
    
    .input-container, .qr-container, .upload-container {
        backdrop-filter: blur(20px);
        background: rgba(255,255,255,0.15);
        border: 1px solid rgba(255,255,255,0.2);
    }
    
    @media (prefers-color-scheme: dark) {
        .input-container, .qr-container, .upload-container {
            background: rgba(0,0,0,0.4);
        }
    }
    """

# App principale
app = rx.App(style=custom_style())
app.add_page(qr_generator)
