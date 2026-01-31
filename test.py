import streamlit as st
import random
import time

# Configuration
st.set_page_config(page_title="Marrakech Runner 🕌", page_icon="🕌", layout="wide")

# Initialisation session_state
def init_game():
    defaults = {
        'score': 0, 'high_score': 0, 'game_active': False, 'player_pos': 1,
        'obstacles': [], 'lives': 3, 'last_update': time.time(), 'game_speed': 0.8
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_game()

# CSS amélioré
st.markdown("""
<style>
.main {background: linear-gradient(135deg, #f5f1e6 0%, #e6dfd1 100%);}
.game-title {text-align:center;color:#C1272D;font-size:3em;font-family:'Georgia',serif;text-shadow:2px 2px 4px rgba(0,0,0,0.3);}
.subtitle {text-align:center;color:#006233;font-size:1.3em;}
.score-display {background:#C1272D;color:white;padding:1rem;border-radius:15px;text-align:center;font-size:1.6em;font-weight:bold;box-shadow:0 6px 12px rgba(0,0,0,0.2);}
.game-container {background:#8B4513;padding:2rem;border-radius:20px;box-shadow:0 10px 20px rgba(0,0,0,0.3);border:4px solid #D4AF37;}
.lane {height:120px;margin:8px 0;border-radius:15px;background:linear-gradient(90deg,#A0522D 33%,#8B4513 66%,#654321 100%);position:relative;box-shadow:inset 0 0 15px rgba(0,0,0,0.4);}
.player {position:absolute;font-size:4em;left:45%;top:20px;transition:all 0.2s;text-shadow:3px 3px 6px rgba(0,0,0,0.6);}
.obstacle {position:absolute;font-size:3.5em;transition:top 0.3s;text-shadow:2px 2px 5px rgba(0,0,0,0.6);}
.controls {display:flex;justify-content:center;gap:25px;margin:25px 0;}
.control-btn {font-size:2.2em;padding:20px 30px;border-radius:50%;border:none;background:linear-gradient(145deg,#D4AF37,#FFD700);cursor:pointer;box-shadow:0 6px 12px rgba(0,0,0,0.3);transition:all 0.15s;}
.control-btn:hover {transform:scale(1.05);}
.control-btn:active {transform:scale(0.95);}
.maroc-theme {background:linear-gradient(135deg,#C1272D,#006233);color:white;padding:15px;border-radius:15px;margin:15px 0;text-align:center;font-weight:bold;}
</style>
""", unsafe_allow_html=True)

# Interface
st.markdown('<h1 class="game-title">🕌 Marrakech Runner</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Guidez le Tajine à travers les ruelles de Marrakech !</p>', unsafe_allow_html=True)

# Score et vies
col1, col2, col3 = st.columns([1, 3, 1])
with col2:
    st.markdown(f'<div class="score-display">Score: {st.session_state.score} | Meilleur: {st.session_state.high_score} | Vies: {"❤️" * st.session_state.lives}</div>', unsafe_allow_html=True)

# Jeu principal
with st.container():
    if not st.session_state.game_active:
        # Écran titre
        st.markdown('<div class="maroc-theme">🎯 Bienvenue dans la Médina de Marrakech !</div>', unsafe_allow_html=True)
        
        if st.button("🚀 COMMENCER L'AVENTURE 🕌", use_container_width=True, type="primary"):
            st.session_state.game_active = True
            st.session_state.score = 0
            st.session_state.lives = 3
            st.session_state.obstacles = []
            st.session_state.player_pos = 1
            st.session_state.last_update = time.time()
            st.rerun()
        
        # Instructions
        st.markdown("""
        <div class="maroc-theme">
        <h3>🎮 RÈGLES DU JEU</h3>
        <ul style="text-align:left;font-size:1.1em;">
            <li>← → Déplacez le Tajine entre les 3 ruelles</li>
            <li>🐪 🏺 Évitez Chameaux & Poteries</li>
            <li>🕌 Mosquée = +50 points bonus !</li>
            <li>Survivez le plus longtemps possible</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    else:
        # Zone de jeu
        st.markdown('<div class="game-container">', unsafe_allow_html=True)
        
        # 3 ruelles
        for lane_idx, lane in enumerate([0, 1, 2]):
            st.markdown(f'<div class="lane" id="lane-{lane}"></div>', unsafe_allow_html=True)
            
            # Joueur
            if lane == st.session_state.player_pos:
                st.markdown('<div class="player">🥘</div>', unsafe_allow_html=True)
            
            # Obstacles visibles seulement
            for obs in st.session_state.obstacles:
                if obs["lane"] == lane and obs["pos"] < 140:
                    emoji = {"chameau": "🐪", "poterie": "🏺", "mosquee": "🕌"}[obs["type"]]
                    st.markdown(f'<div class="obstacle" style="top:{obs["pos"]}px;left:45%;">{emoji}</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Contrôles
        col_left, col_pause, col_right = st.columns([1, 1, 1])
        with col_left:
            if st.button("← GAUCHE", key="left", help="Ruelles gauche"):
                if st.session_state.player_pos > 0:
                    st.session_state.player_pos -= 1
                    st.rerun()
        with col_pause:
            if st.button("⏸️ PAUSE", key="pause"):
                st.session_state.game_active = False
                st.rerun()
        with col_right:
            if st.button("DROITE →", key="right", help="Ruelles droite"):
                if st.session_state.player_pos < 2:
                    st.session_state.player_pos += 1
                    st.rerun()
        
        # Logique de jeu (mise à jour contrôlée)
        now = time.time()
        if now - st.session_state.last_update > st.session_state.game_speed:
            st.session_state.last_update = now
            
            # Ajouter obstacle (20% chance)
            if random.random() < 0.2:
                st.session_state.obstacles.append({
                    "lane": random.randint(0, 2),
                    "pos": -20,
                    "type": random.choice(["chameau", "poterie", "mosquee"])
                })
            
            # Mettre à jour obstacles
            new_obstacles = []
            for obs in st.session_state.obstacles:
                obs["pos"] += 25  # Vitesse
                
                # Collision (zone joueur: 20-80px)
                if (obs["lane"] == st.session_state.player_pos and 
                    20 <= obs["pos"] <= 80):
                    
                    if obs["type"] == "mosquee":
                        st.session_state.score += 50
                        st.success("🕌 Bonus Mosquée ! +50 pts")
                    else:
                        st.session_state.lives -= 1
                        st.error(f"💥 {obs['type'].title()} !")
                    
                    if st.session_state.lives <= 0:
                        st.session_state.high_score = max(st.session_state.high_score, st.session_state.score)
                        st.session_state.game_active = False
                        st.rerun()
                    continue  # Ne pas ajouter cet obstacle
                
                # Garder si visible
                if obs["pos"] < 140:
                    new_obstacles.append(obs)
                else:
                    st.session_state.score += 10  # Points survie
            
            st.session_state.obstacles = new_obstacles
            
            # Difficulté progressive
            if st.session_state.score > 150:
                st.session_state.game_speed = 0.4
            elif st.session_state.score > 75:
                st.session_state.game_speed = 0.6
            
            st.rerun()

# Footer
st.markdown("---")
st.markdown('<div style="text-align:center;color:#666;">🇲🇦 Marrakech Runner - Python & Streamlit 🕌</div>', unsafe_allow_html=True)
