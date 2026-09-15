# GAUCHE : Composition visuelle officielle
    with col_left:
        st.markdown(f"""
            <div class="dalkia-hero-card">
                <!-- Étoile filante dorée en SVG vectoriel -->
                <svg width="220" height="220" viewBox="0 0 200 200" style="position: absolute; left: -20px; top: 10px; opacity: 0.85;">
                    <polygon points="100,10 125,70 190,75 140,120 155,185 100,150 45,185 60,120 10,75 75,70" 
                             fill="none" stroke="#D4AF37" stroke-width="4" />
                    <polygon points="90,20 112,72 170,77 126,117 139,173 90,140 41,173 54,117 10,77 68,72" 
                             fill="none" stroke="#C0C0C0" stroke-width="2.5" opacity="0.6" />
                </svg>

                <div style="z-index: 2; text-align: right; width: 100%;">
                    <img src="{URL_LOGO_DALKIA}" width="180" style="margin-bottom: 20px;">
                </div>
                
                <div style="z-index: 2; text-align: center; margin-top: 10px;">
                    <h1 class="title-dalkia-green">BUDGET PARTICIPATIF</h1>
                    <h1 class="subtitle-dalkia-blue">2027</h1>
                </div>
            </div>
        """, unsafe_allow_html=True)  # <-- C'est ce paramètre qui manque
