# GAUCHE : Visuel d'accueil avec la photo de la tour Dalkia
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
