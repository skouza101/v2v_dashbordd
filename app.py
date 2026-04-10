import streamlit as st
import time
import random
import pandas as pd
from datetime import datetime
try:
    import cv2
except ImportError:
    cv2 = None

# ==========================================
# INITIALISATION DE L'ÉTAT (SESSION STATE)
# ==========================================
if 'auth_status' not in st.session_state:
    st.session_state.auth_status = False
if 'vitesse' not in st.session_state:
    st.session_state.vitesse = 10
if 'distance' not in st.session_state:
    st.session_state.distance = 3.0
if 'convoi_status' not in st.session_state:
    st.session_state.convoi_status = 'STOPPED'
if 'journal' not in st.session_state:
    st.session_state.journal = [
        f"{datetime.now().strftime('%H:%M:%S')} - Système initialisé"
    ]
if 'alertes' not in st.session_state:
    st.session_state.alertes = []
if 'telemetry' not in st.session_state:
    st.session_state.telemetry = pd.DataFrame(columns=["Temps", "Vitesse_Reelle", "Distance_Reelle"])
if 'gps_data' not in st.session_state:
    st.session_state.gps_data = pd.DataFrame({"lat": [48.8566], "lon": [2.3522]})
if 'current_speed' not in st.session_state:
    st.session_state.current_speed = 0.0
if 'current_dist' not in st.session_state:
    st.session_state.current_dist = 3.0

def log_event(message):
    timestamp = datetime.now().strftime('%H:%M:%S')
    st.session_state.journal.insert(0, f"{timestamp} - {message}")
    if len(st.session_state.journal) > 15:
        st.session_state.journal.pop()

def simulate_step():
    # Simulate perfect real-time tracking
    if st.session_state.convoi_status == 'RUNNING':
        st.session_state.current_speed = st.session_state.vitesse
        st.session_state.current_dist = st.session_state.distance
        st.session_state.gps_data.loc[0, 'lat'] += random.uniform(-0.00005, 0.00005)
        st.session_state.gps_data.loc[0, 'lon'] += random.uniform(-0.00005, 0.00005)
    else:
        # Gradually decelerate or return to target if stopped
        st.session_state.current_speed = 0.0
        st.session_state.current_dist = st.session_state.distance
        
    new_data = pd.DataFrame({
        "Temps": [datetime.now().strftime('%H:%M:%S')],
        "Vitesse_Reelle": [st.session_state.current_speed],
        "Distance_Reelle": [st.session_state.current_dist]
    })
    st.session_state.telemetry = pd.concat([st.session_state.telemetry, new_data], ignore_index=True)
    if len(st.session_state.telemetry) > 50:
        st.session_state.telemetry = st.session_state.telemetry.tail(50)

# ==========================================
# DESIGN THEME TACTIQUE / MILITAIRE (CSS)
# ==========================================
def apply_css():
    import os
    if os.path.exists("camo_bg.png"):
        import base64
        with open("camo_bg.png", "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
            st.markdown(
                f"<style>.stApp {{ background-image: url('data:image/png;base64,{encoded_string}'); background-size: 400px; background-repeat: repeat; background-attachment: fixed; }}</style>",
                unsafe_allow_html=True
            )

    st.markdown("""
        <style>
        /* Base background and main font */
        .stApp {
            background-color: #1a1e18; /* Dark military gray/olive */
            color: #d8decb;
        }
        
        /* Headers and titles */
        h1, h2, h3 {
            color: #f1f5eb !important;
            font-weight: 800 !important;
        }
        
        /* Custom styled alerts */
        .alert-panel {
            background-color: #3b1c1c;
            border-left: 5px solid #ff4444;
            padding: 10px;
            margin-bottom: 10px;
            border-radius: 4px;
        }
        .warning-panel {
            background-color: #3b2f1c;
            border-left: 5px solid #ffbb33;
            padding: 10px;
            margin-bottom: 10px;
            border-radius: 4px;
        }
        .info-panel {
            background-color: #1c2b3b;
            border-left: 5px solid #33b5e5;
            padding: 10px;
            margin-bottom: 10px;
            border-radius: 4px;
        }
        .success-panel {
            background-color: #1c3b24;
            border-left: 5px solid #00C851;
            padding: 10px;
            margin-bottom: 10px;
            border-radius: 4px;
        }

        /* Tactical Button styling */
        .stButton > button {
            background-color: #2b3626;
            color: white;
            border: 2px solid #556b4b;
            border-radius: 8px;
            font-weight: bold;
            text-transform: uppercase;
        }
        .stButton > button:active {
            background-color: #556b4b;
        }
        
        /* Button coloring overrides based on standard classes (if Streamlit types are used) */
        button[kind="primary"] {
            background-color: #9c1c1c !important; /* Urgent Red */
            border-color: #ff3333 !important;
            font-size: 1.1em;
        }
        
        hr {
            margin-top: 1em;
            margin-bottom: 1em;
            border: 0;
            border-top: 2px solid #4a5c40;
        }
        </style>
    """, unsafe_allow_html=True)

# ==========================================
# WIDGETS PERSONNALISÉS HTML
# ==========================================
def draw_convoy_diagram():
    # Croquis visuel du convoi
    html = f"""
    <div style='background: #10140e; padding: 25px; border-radius: 10px; border: 2px solid #2e3a24; text-align: center; box-shadow: inset 0 0 15px rgba(0,0,0,0.8); white-space: nowrap; overflow-x: auto;'>
        <div style='display: inline-block; padding: 25px 10px; background: #1c4516; border: 3px solid #6b9e4a; border-radius: 12px; color: white; font-weight: bold; font-size: 1.4em; width: 170px; box-shadow: 0 0 15px rgba(76, 175, 80, 0.4); margin: 0 5px; vertical-align: middle;'>
            🚛 LEADER
        </div>
        <span style='color: #8da675; font-weight: bold; font-size: 1.1em; margin: 0 5px; vertical-align: middle;'>--- {st.session_state.distance} m ---▶</span>
        <div style='display: inline-block; padding: 12px; background: #3d4a34; border: 2px solid #5a7547; border-radius: 8px; color: lightgray; width: 120px; font-size: 0.9em; margin: 0 5px; vertical-align: middle;'>
            🛻 SUIVEUR 1
        </div>
        <span style='color: #8da675; font-weight: bold; font-size: 1.1em; margin: 0 5px; vertical-align: middle;'>--- {st.session_state.distance} m ---▶</span>
        <div style='display: inline-block; padding: 12px; background: #3d4a34; border: 2px solid #5a7547; border-radius: 8px; color: lightgray; width: 120px; font-size: 0.9em; margin: 0 5px; vertical-align: middle;'>
            🛻 SUIVEUR 2
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

# ==========================================
# ONGLETS (TABS)
# ==========================================

def interface_supervision():
    col1, spacer, col2 = st.columns([5, 0.2, 3])
    
    with col1:
        st.subheader("Croquis du Convoi")
        draw_convoy_diagram()
        
        st.markdown("<br>", unsafe_allow_html=True)
        cA, cB, cC = st.columns(3)
        
        cA.metric("Vitesse Actuelle", f"{st.session_state.current_speed:.1f} km/h")
        cB.metric("Distance Actuelle", f"{st.session_state.current_dist:.1f} m")
        cC.metric("État Communication", "OK", delta="Stable 12ms", delta_color="normal")
        
        status_msg = "🟢 EN MOUVEMENT" if st.session_state.convoi_status == "RUNNING" else "🔴 À L'ARRÊT"
        if st.session_state.convoi_status == 'EMERGENCY':
            status_msg = "🚨 ARRÊT D'URGENCE"
        st.markdown(f"**État du Convoi:** {status_msg}")
        
    with col2:
        st.subheader("Localisation GPS Leader")
        st.map(st.session_state.gps_data, zoom=16, height=220)
        
    st.markdown("---")
    st.subheader("📈 Télémétrie en Temps Réel")
    tcol1, tcol2 = st.columns(2)
    with tcol1:
        st.caption("Vitesse du Leader (km/h)")
        if not st.session_state.telemetry.empty:
            st.area_chart(st.session_state.telemetry.set_index('Temps')['Vitesse_Reelle'], color="#ffaa00", height=200)
        else:
            st.info("En attente de données...")
            
    with tcol2:
        st.caption("Distance de Suivi (m)")
        if not st.session_state.telemetry.empty:
            st.line_chart(st.session_state.telemetry.set_index('Temps')['Distance_Reelle'], color="#00ffaa", height=200)
        else:
            st.info("En attente de données...")


def interface_commande():
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Vitesse (km/h)")
        nv_vitesse = st.slider("Contrôle Vitesse", 0, 100, st.session_state.vitesse, label_visibility="collapsed")
        if nv_vitesse != st.session_state.vitesse:
            st.session_state.vitesse = nv_vitesse
            log_event(f"Vitesse modifiée: {nv_vitesse} km/h")
            
    with col2:
        st.subheader("Distance (m)")
        nv_dist = st.slider("Contrôle Distance", 1.0, 15.0, float(st.session_state.distance), 0.5, label_visibility="collapsed")
        if nv_dist != st.session_state.distance:
            st.session_state.distance = nv_dist
            log_event(f"Distance régulée: {nv_dist} m")
            
    st.markdown("---")
    st.subheader("Panneau de Contrôle Central")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("▶️ DÉMARRER LE CONVOI", use_container_width=True):
            st.session_state.convoi_status = 'RUNNING'
            log_event("Démarrage du convoi")
    with c2:
        if st.button("⏹️ ARRÊTER LE CONVOI", use_container_width=True):
            st.session_state.convoi_status = 'STOPPED'
            log_event("Arrêt progressif du convoi")
    with c3:
        if st.button("⚠️ ARRÊT D'URGENCE", type="primary", use_container_width=True):
            st.session_state.convoi_status = 'EMERGENCY'
            st.session_state.vitesse = 0
            log_event("ARRÊT D'URGENCE DÉCLENCHÉ")
            
    st.markdown("---")
    st.subheader("Actions Avancées")
    t1, t2, t3, t4 = st.columns(4)
    with t1:
        if st.button("◀️ Tourner Gauche", use_container_width=True):
            log_event("Action: Virage à gauche")
    with t2:
        if st.button("▶️ Tourner Droite", use_container_width=True):
            log_event("Action: Virage à droite")
    with t3:
        if st.button("➕ Ajouter Suiveur", use_container_width=True):
            log_event("Action: Procédure d'ajout suiveur")
    with t4:
        if st.button("➖ Retirer Suiveur", use_container_width=True):
            log_event("Action: Procédure retrait suiveur")


def interface_systeme():
    col1, spacer, col2 = st.columns([4, 0.2, 5])
    
    with col1:
        st.subheader("Alertes Actives")
        
        # HTML custom styling based on mockups
        st.markdown("<div class='alert-panel'>🚨 <b>OBSTACLE DÉTECTÉ</b><br>À 15m devant le Leader (CRITIQUE)</div>", unsafe_allow_html=True)
        st.markdown("<div class='warning-panel'>⚠️ <b>PERTE DE COMMUNICATION</b><br>Instabilité Véhicule 2 (ATTENTION)</div>", unsafe_allow_html=True)
        st.markdown("<div class='info-panel'>💧 <b>DÉTECTION DE PLUIE</b><br>Mode Sécurité Activé (INFO)</div>", unsafe_allow_html=True)
        st.markdown("<div class='success-panel'>✅ <b>VÉHICULE 3 AJOUTÉ</b><br>Au convoi avec succès (OK)</div>", unsafe_allow_html=True)
        
        if st.button("Acquitter les alertes", use_container_width=True):
            log_event("Toutes les alertes ont été acquittées")

    with col2:
        st.subheader("État des senseurs")
        s1, s2 = st.columns(2)
        with s1:
            st.markdown("- **Caméra Raspberry Pi:** Actif")
            st.markdown("- **Détecteur d'Obstacle:** Actif")
            st.markdown("- **Suiveur de Ligne:** Actif")
        with s2:
            st.markdown("- **Détecteur de Pluie:** OUI")
            st.markdown("- **Batterie Lead:** 87%")
            st.markdown("- **Liaison V2V:** 12 ms")
            
        st.markdown("---")
        st.subheader("Journal des Événements")
        journal_text = "\\n".join(st.session_state.journal)
        st.text_area("Logs Système (Derniers événements)", value=journal_text, height=200, disabled=True)

def interface_vision():
    st.subheader("Flux Vidéo en Temps Réel - Caméra")
    st.markdown("Cette interface permet de visualiser le flux embarqué et de détecter automatiquement les objets.")
    
    col_cam, col_settings = st.columns([7, 3])
    with col_settings:
        run_cam = st.toggle("Activer la Caméra", value=False)
        st.info("💡 **Mode Détection:** Activé\n\nL'algorithme de vision identifie les obstacles et les encadre automatiquement en vert.")
    with col_cam:
        FRAME_WINDOW = st.empty()
        if run_cam:
            if cv2 is None:
                st.error("⚠️ La bibliothèque 'opencv-python' est en cours d'installation, veuillez patienter.")
            else:
                try:
                    cap = cv2.VideoCapture(0) # Caméra du Mac
                    # Détection basique pour l'exemple
                    cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
                    
                    while run_cam:
                        ret, frame = cap.read()
                        if not ret:
                            st.error("Erreur de flux vidéo.")
                            break
                        
                        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                        objects = cascade.detectMultiScale(gray, 1.3, 5)
                        
                        for (x, y, w, h) in objects:
                            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 3)
                            cv2.putText(frame, "OBJET", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                            
                        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        FRAME_WINDOW.image(frame_rgb)
                        time.sleep(0.05)
                    cap.release()
                except Exception as e:
                    st.error(f"Erreur: {e}")
        else:
            FRAME_WINDOW.info("Caméra inactive. Basculez le bouton pour démarrer le direct.")

# ==========================================
# APPLICATION PRINCIPALE
# ==========================================
def authenticate():
    st.markdown("<br><br><h2 style='text-align:center;'>🔒 ACCÈS MILITAIRE SÉCURISÉ REQUIS</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#8da675;'>Veuillez entrer vos identifiants d'opérateur pour contrôler le convoi.</p>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.markdown("<div style='background-color: #2b3626; padding: 20px; border-radius: 10px; border: 2px solid #4a5c40;'>", unsafe_allow_html=True)
        with st.form("login_form"):
            pwd = st.text_input("Code d'Accès Tactique", type="password", placeholder="Entrez le code...")
            submitted = st.form_submit_button("DÉVERROUILLER 🔓", use_container_width=True)
            if submitted:
                if pwd == "arm2026":
                    st.session_state.auth_status = True
                    st.rerun()
                else:
                    st.error("❌ Code invalide. Accès refusé.")
        st.markdown("</div>", unsafe_allow_html=True)

def main():
    st.set_page_config(page_title="Système de Convoi Intelligent", layout="wide", page_icon="🛡️")
    apply_css()
    
    if not st.session_state.auth_status:
        authenticate()
        return
        
    simulate_step()  # Advance simulation state on each UI interaction
    
    # Top Bar Header like a tactical interface
    c_img, c_title, c_stats = st.columns([1, 6, 2])
    with c_img:
        try:
            st.image("logo.png")
        except Exception:
            st.markdown("<h1 style='text-align: right;'>🛡️</h1>", unsafe_allow_html=True)
    with c_title:
        st.markdown("<h1>SYSTÈME DE CONVOI INTELLIGENT</h1>", unsafe_allow_html=True)
        st.markdown("<span style='color: #8da675; font-weight: bold;'>INTERFACE DE GESTION TACTIQUE</span>", unsafe_allow_html=True)
    with c_stats:
        st.markdown(f"🖥️ **V2V Link:** OK<br>🔋 **Batt:** 87%<br>🕒 **Time:** {datetime.now().strftime('%H:%M')}", unsafe_allow_html=True)
        
    st.markdown("---")
    
    # Navigation avec onglets
    tab1, tab2, tab3, tab4 = st.tabs([
        "👁️ SUPERVISION DU CONVOI", 
        "⚙️ INTERFACE DE COMMANDE", 
        "⚠️ SYSTÈME (ALERTES ET MESSAGES)",
        "📷 VISION CAMÉRA"
    ])
    
    with tab1:
        interface_supervision()
        
    with tab2:
        interface_commande()
        
    with tab3:
        interface_systeme()
        
    with tab4:
        interface_vision()

if __name__ == "__main__":
    main()
