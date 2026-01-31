import streamlit as st
import random
import time

# Configuration de la page
st.set_page_config(
    page_title="Marrakech Runner",
    page_icon="🕌",
    layout="centered"
)

# Initialisation de l'état du jeu
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'game_active' not in st.session_state:
    st.session_state.game_active = False
if 'player_pos' not in st.session_state:
    st.session_state.player_pos = 1  # 0=Gauche, 1=Centre, 2=Droite
if 'obstacles' not in st.session_state:
    st.session_state.obstacles = []
if 'game_speed' not in st.session_state:
    st.session_state.game_speed = 0.5
if 'lives' not in st.session_state:
    st.session_state.lives = 3

# Styles CSS pour l'apparence marocaine
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #f5f1e6 0%, #e6dfd1 100%);
    }
    .game-title {
        text-align: center;
        color: #C1272D;
        font-family: 'Georgia', serif;
        font-size: 3.5em;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        margin-bottom: 0.2em;
    }
    .subtitle {
        text-align: center;
        color: #006233;
        font-family: 'Arial', sans-serif;
        font-size: 1.2em;
        margin-bottom: 2em;
    }
    .score-display {
        background-color: #C1272D;
        color: white;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        font-size: 1.5em;
        font-weight: bold;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .lives-display {
        color: #C1272D;
        font-size: 1.8em;
        text-align: center;
        margin: 10px 0;
    }
    .game-container {
        background-color: #8B4513;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.2);
        border: 5px solid #D4AF37;
    }
    .lane {
        height: 100px;
        margin: 5px 0;
        border-radius: 10px;
        position: relative;
        background: linear-gradient(90deg, #a0522d 0%, #8b4513 100%);
        box-shadow: inset 0 0 10px rgba(0,0,0,0.5);
    }
    .player {
        position: absolute;
        font-size: 3.5em;
        transition: left 0.2s;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }
    .obstacle {
        position: absolute;
        font-size: 3em;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }
    .controls {
        display: flex;
        justify-content: center;
        gap: 20px;
        margin-top: 20px;
    }
    .control-btn {
        font-size: 2em;
        padding: 15px 25px;
        border-radius: 50%;
        border: none;
        background: linear-gradient(145deg, #D4AF37, #FFD700);
        cursor: pointer;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        transition: transform 0.1s;
    }
    .control-btn:active {
        transform: scale(0.95);
    }
    .maroc-theme {
        background: linear-gradient(135deg, #C1272D 0%, #006233 100%);
        color: white;
        padding: 10px;
        border-radius: 10px;
        margin: 5px 0;
        text-align: center;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Titre du jeu
st.markdown('<h1 class="game-title">🕌 Marrakech Runner</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Guidez le Tajine à travers les ruelles animées de Marrakech !</p>', unsafe_allow_html=True)

# Affichage du score et des vies
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown(f'<div class="score-display">🕌 Score: {st.session_state.score} | 🏆 Meilleur: {st.session_state.get("high_score", 0)}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="lives-display">{"❤️" * st.session_state.lives}</div>', unsafe_allow_html=True)

# Conteneur du jeu
game_container = st.container()

with game_container:
    if not st.session_state.game_active:
        # Écran de démarrage
        st.markdown('<div class="maroc-theme">🎯 Bienvenue à Marrakech !</div>', unsafe_allow_html=True)
        st.image("https://i.imgur.com/V0p7wVD.png", caption="Ruelles de la Médina", use_column_width=True)
        
        col1, col2, col3 = st.columns(3)
        with col2:
            if st.button("🚀 Commencer l'Aventure", use_container_width=True, type="primary"):
                st.session_state.game_active = True
                st.session_state.score = 0
                st.session_state.lives = 3
                st.session_state.obstacles = []
                st.session_state.player_pos = 1
                st.rerun()
        
        st.markdown("""
        <div class="maroc-theme">
        <h3>🎮 Comment jouer :</h3>
        <p>• Utilisez les flèches ← → pour déplacer le Tajine</p>
        <p>• Évitez les obstacles dans les ruelles</p>
        <p>• Collectez des points en survivant le plus longtemps</p>
        <p>• Vous avez 3 vies !</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Thèmes marocains
        st.markdown("""
        <div style="background-color: #f5f1e6; padding: 15px; border-radius: 10px; margin-top: 20px;">
        <h3 style="color: #C1272D; text-align: center;">🏺 Éléments Marocains :</h3>
        <div style="display: flex; justify-content: space-around; text-align: center;">
            <div>
                <div style="font-size: 2.5em;">🥘</div>
                <div>Tajine (Vous)</div>
            </div>
            <div>
                <div style="font-size: 2.5em;">🐪</div>
                <div>Chameau (Obstacle)</div>
            </div>
            <div>
                <div style="font-size: 2.5em;">🏺</div>
                <div>Poterie (Obstacle)</div>
            </div>
            <div>
                <div style="font-size: 2.5em;">🕌</div>
                <div>Mosquée (Bonus)</div>
            </div>
        </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Zone de jeu
        st.markdown('<div class="game-container">', unsafe_allow_html=True)
        
        # Création des 3 voies (ruelles)
        lanes = [0, 1, 2]
        lane_positions = {0: "15%", 1: "45%", 2: "75%"}
        
        for lane in lanes:
            lane_div = f'<div class="lane" id="lane-{lane}"></div>'
            st.markdown(lane_div, unsafe_allow_html=True)
            
            # Afficher le joueur dans la bonne voie
            if lane == st.session_state.player_pos:
                player_emoji = "🥘"  # Tajine
                st.markdown(
                    f'<div class="player" style="left: {lane_positions[lane]};">{player_emoji}</div>',
                    unsafe_allow_html=True
                )
            
            # Afficher les obstacles
            for obstacle in st.session_state.obstacles:
                if obstacle["lane"] == lane:
                    obstacle_type = obstacle["type"]
                    emoji_map = {
                        "chameau": "🐪",
                        "poterie": "🏺",
                        "mosquee": "🕌"
                    }
                    obstacle_emoji = emoji_map.get(obstacle_type, "❌")
                    position = obstacle["position"]
                    
                    if 0 <= position < 100:  # Afficher seulement les obstacles visibles
                        st.markdown(
                            f'<div class="obstacle" style="left: {lane_positions[lane]}; top: {position}px;">{obstacle_emoji}</div>',
                            unsafe_allow_html=True
                        )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Contrôles de déplacement
        st.markdown('<div class="controls">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.button("←", key="left", use_container_width=True, help="Aller à gauche"):
                if st.session_state.player_pos > 0:
                    st.session_state.player_pos -= 1
                    st.rerun()
        
        with col2:
            if st.button("⏸️", key="pause", use_container_width=True, help="Pause"):
                st.session_state.game_active = False
                st.rerun()
        
        with col3:
            if st.button("→", key="right", use_container_width=True, help="Aller à droite"):
                if st.session_state.player_pos < 2:
                    st.session_state.player_pos += 1
                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Logique du jeu
        if st.session_state.game_active:
            # Ajouter de nouveaux obstacles aléatoirement
            if random.random() < 0.3:  # 30% de chance d'ajouter un obstacle
                obstacle_type = random.choice(["chameau", "poterie", "mosquee"])
                st.session_state.obstacles.append({
                    "lane": random.randint(0, 2),
                    "position": 0,
                    "type": obstacle_type
                })
            
            # Déplacer les obstacles vers le bas
            for obstacle in st.session_state.obstacles[:]:
                obstacle["position"] += 20
                
                # Vérifier les collisions
                if (obstacle["lane"] == st.session_state.player_pos and 
                    40 <= obstacle["position"] <= 80):
                    if obstacle["type"] == "mosquee":
                        st.session_state.score += 50  # Bonus
                        st.toast("🕌 Bonus mosquée! +50 points!", icon="🎉")
                    else:
                        st.session_state.lives -= 1
                        st.toast(f"💥 Collision avec {obstacle['type']}!", icon="⚠️")
                    
                    st.session_state.obstacles.remove(obstacle)
                    
                    if st.session_state.lives <= 0:
                        st.session_state.game_active = False
                        if st.session_state.score > st.session_state.get("high_score", 0):
                            st.session_state.high_score = st.session_state.score
                        st.toast(f"🏁 Game Over! Score final: {st.session_state.score}", icon="💔")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.rerun()
                
                # Supprimer les obstacles hors écran
                if obstacle["position"] > 100:
                    st.session_state.obstacles.remove(obstacle)
                    st.session_state.score += 10
            
            # Augmenter la difficulté
            if st.session_state.score > 100 and st.session_state.game_speed > 0.3:
                st.session_state.game_speed = 0.4
            elif st.session_state.score > 200 and st.session_state.game_speed > 0.2:
                st.session_state.game_speed = 0.3
            
            # Mettre à jour le jeu automatiquement
            time.sleep(st.session_state.game_speed)
            st.rerun()

# Pied de page
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9em;">
<p>🎮 Jeu créé avec Python & Streamlit | Thème Marocain 🇲🇦</p>
<p>🥘 Évitez les obstacles dans les ruelles de Marrakech !</p>
</div>
""", unsafe_allow_html=True)
