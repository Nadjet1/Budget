# --- ACCUEIL : PHOTO INSTITUTIONNELLE À GAUCHE, CONNEXION À DROITE ---
if 'connecte' not in st.session_state:
    st.session_state.connecte = False

if not st.session_state.connecte:
    st.markdown("""<style>section[data-testid="stSidebar"] {display: none;}</style>""", unsafe_allow_html=True)
    
    col_left, col_right = st.columns([1.1, 1], gap="large")
    
    # 4 espaces d'indentation sous `if not st.session_state.connecte:`
    with col_left:
        st.markdown(f"""
            <div class="dalkia-cover-card">
                <div>
                    <span style="border-left: 3px solid #6FA247; padding-left: 8px; font-size: 11px; font-weight: 800; letter-spacing: 1px; color: #FFFFFF; text-transform: uppercase;">
                        STRATÉGIE GROUPE EDF
                    </span>
                </div>
                
                <div style="margin-top: 180px;">
                    <div style="font-size: 38px; font-weight: 900; letter-spacing: -1px; line-height: 1; color: white;">
                        dalkia
                    </div>
                    <div style="font-size: 13px; font-weight: 700; letter-spacing: 2px; color: #E2E8F0; margin-bottom: 20px;">
                        GROUPE <b>edf</b>
                    </div>
                    <p style="font-size: 13px; opacity: 0.9; margin: 0; line-height: 1.4; max-width: 90%;">
                        Accompagner la transition énergétique et numérique à travers nos territoires.
                    </p>
                </div>
            </div>
        """, unsafe_allow_html=True)

    with col_right:
        with st.form("form_login_photo"):
            st.image(URL_LOGO_DALKIA, width=170)
            st.markdown("<h3 style='color: #6FA247; font-weight: 700; margin-top: 15px; margin-bottom: 2px;'>Budget Participatif 2027</h3>", unsafe_allow_html=True)
            st.markdown("<p style='color: #666; font-size: 13px; margin-bottom: 20px;'>Accès au portail de gestion & arbitrage des CAPAs</p>", unsafe_allow_html=True)
            
            identifiant = st.text_input("Identifiant", placeholder="ex: vmo ou nhachemi").lower()
            mdp = st.text_input("Mot de passe", type="password", placeholder="••••••••")
            
            st.markdown("<br>", unsafe_allow_html=True)
            submit_login = st.form_submit_button("Se connecter ➔")
            
            if submit_login:
                if identifiant in UTILISATEURS and UTILISATEURS[identifiant]["mdp"] == mdp:
                    st.session_state.connecte = True
                    st.session_state.utilisateur = UTILISATEURS[identifiant]["nom"]
                    st.session_state.profil = UTILISATEURS[identifiant]["profil"]
                    st.rerun()
                else:
                    st.error("❌ Identifiants incorrects.")

    st.stop()
