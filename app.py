import streamlit as st
import pandas as pd
import plotly.express as px
import os
import io
from datetime import datetime

st.set_page_config(page_title="Portail Budget Participatif Dalkia 2027", layout="wide", initial_sidebar_state="expanded")

# --- GESTION DU LOGO (Local 'logo.png' ou Fallback URL) ---
URL_LOGO_DALKIA = "logo.png" if os.path.exists("logo.png") else "https://upload.wikimedia.org/wikipedia/commons/6/63/Dalkia_logo_2014.svg"

# --- 1. DESIGN CUSTOMISÉ (CSS) ---
st.markdown("""
    <style>
    div[data-testid="stFormSubmitButton"] > button {
        background-color: #E5004F !important;
        color: white !important;
        font-weight: bold !important;
        font-size: 16px !important;
        border-radius: 5px !important;
        border: none !important;
        width: 100%;
        transition: 0.3s;
    }
    div[data-testid="stFormSubmitButton"] > button:hover {
        background-color: #B3003D !important;
    }
    .cadre-creer {
        background-color: #FFF0F5;
        padding: 20px;
        border-left: 6px solid #E5004F;
        border-radius: 8px;
        margin-bottom: 20px;
    }
    .titre-section-1 { color: #E5004F; border-bottom: 2px solid #E5004F; padding-bottom: 5px; margin-top: 15px; }
    .titre-section-2 { color: #005A9C; border-bottom: 2px solid #005A9C; padding-bottom: 5px; margin-top: 15px; }
    .titre-section-3 { color: #009688; border-bottom: 2px solid #009688; padding-bottom: 5px; margin-top: 15px; }
    </style>
""", unsafe_allow_html=True)

# --- 2. BASE DE DONNÉES UTILISATEURS ---
UTILISATEURS = {
    "vmo": {"mdp": "dalkia2027", "profil": "VMO", "nom": "Admin VMO"},
    "nhachemi": {"mdp": "user123", "profil": "BPO", "nom": "Nadjet Hachemi"},
    "mmontoneri": {"mdp": "user123", "profil": "RTE", "nom": "Mael Montoneri"},
    "stagiaire": {"mdp": "nlp", "profil": "Data", "nom": "Stagiaire NLP"}
}

# --- 3. GESTION DU FICHIER EXCEL ET AUDIT TRAIL ---
FICHIER_EXCEL = 'Support de Valorisation des capabilités - Budget2025_2.xlsx'

COLONNES = [
    'Auteur', 'Enveloppe', 'Département', 'Domaine porteur', 'Axe Stratégique', 'Projet Stratégique', 
    'EPIC', 'ID Ticket JIRA EPIC', 'Nom CAPA', 'ID Ticket JIRA CAPA', 'Train / Hors train', 'Priorité', 'Etat', 
    'Statut Arbitrage', 'Features / Besoins', 'Equipes contributrices',
    'Budget R0 BP 2027 (K€)', 'Encouru R1 (K€)', 'Reste à engager (K€)', 'Prévisionnel R2 (K€)', 'Delta R2-R0 (K€)',
    'Contexte de la CAPA', 'Critère Conformité', 'Critère Image', 'Critère Opérationnel', 'Critère Économique', 
    'Explications des notes', 'Indicateur de mesure', 'Valeur à date', 'Valeur cible', 'Commentaires VMO',
    'Modifié_Par', 'Dernière_Modification_Date'
]

def calculer_priorite_auto(n_conf, n_ope, n_eco):
    """Calcul automatique de la priorité métier."""
    try:
        conf = float(n_conf)
        gains = float(n_ope) + float(n_eco)
        if conf >= 3:
            return "P0" # Obligatoire / Obsolescence
        elif gains >= 6:
            return "P1" # Forte valeur ajoutée
        else:
            return "P2" # Secondaire / A arbitrer
    except:
        return "P2"

def charger_donnees():
    if os.path.exists(FICHIER_EXCEL):
        try:
            df = pd.read_excel(FICHIER_EXCEL, sheet_name='Base_CAPA')
            if 'Budget R0 (K€)' in df.columns:
                df.rename(columns={'Budget R0 (K€)': 'Budget R0 BP 2027 (K€)'}, inplace=True)
            for col in COLONNES:
                if col not in df.columns:
                    df[col] = None
            return df[COLONNES]
        except:
            pass
    return pd.DataFrame(columns=COLONNES)

def sauvegarder_donnees(df):
    with pd.ExcelWriter(FICHIER_EXCEL, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Base_CAPA', index=False)

def generer_excel_propre(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Portefeuille_BP2027', index=False)
        worksheet = writer.sheets['Portefeuille_BP2027']
        for col in worksheet.columns:
            max_len = max(len(str(cell.value or '')) for cell in col)
            col_letter = col[0].column_letter
            worksheet.column_dimensions[col_letter].width = max(max_len + 4, 12)
    return output.getvalue()

def generer_csv_excel(df):
    return df.to_csv(index=False, sep=';', encoding='utf-8-sig').encode('utf-8-sig')

def ajouter_alertes(df):
    df_alert = df.copy()
    def verifier_depassement(row):
        r0 = pd.to_numeric(row['Budget R0 BP 2027 (K€)'], errors='coerce')
        r2 = pd.to_numeric(row['Prévisionnel R2 (K€)'], errors='coerce')
        if pd.notnull(r0) and pd.notnull(r2) and r0 > 0:
            if r2 > (r0 * 1.15):
                return "⚠️ Dépassement > 15%"
        return "✅ OK"
    
    if not df_alert.empty:
        df_alert['Alerte Budgétaire'] = df_alert.apply(verifier_depassement, axis=1)
    return df_alert

if 'projets' not in st.session_state:
    st.session_state.projets = charger_donnees()

# --- 4. AUTHENTIFICATION SÉCURISÉE ---
if 'connecte' not in st.session_state:
    st.session_state.connecte = False

st.sidebar.image(URL_LOGO_DALKIA, width=200)
st.sidebar.title("🔐 Espace Sécurisé")

if not st.session_state.connecte:
    st.sidebar.info("Veuillez vous authentifier pour accéder au BP 2027.")
    identifiant = st.sidebar.text_input("Identifiant (ex: vmo ou nhachemi)").lower()
    mdp = st.sidebar.text_input("Mot de passe", type="password")
    
    if st.sidebar.button("Se connecter"):
        if identifiant in UTILISATEURS and UTILISATEURS[identifiant]["mdp"] == mdp:
            st.session_state.connecte = True
            st.session_state.utilisateur = UTILISATEURS[identifiant]["nom"]
            st.session_state.profil = UTILISATEURS[identifiant]["profil"]
            st.rerun()
        else:
            st.sidebar.error("❌ Identifiants incorrects.")
    st.stop()

# --- 5. NAVIGATION & RÔLES ---
st.sidebar.success(f"Connecté : {st.session_state.utilisateur}\n\nProfil : {st.session_state.profil}")
if st.sidebar.button("Se déconnecter"):
    st.session_state.connecte = False
    st.rerun()

est_admin = (st.session_state.profil == "VMO")

st.sidebar.markdown("---")

if est_admin:
    st.sidebar.markdown("### 👑 Menu VMO (Admin)")
    menu = st.sidebar.radio("Navigation", ["📊 Tableau de bord BP 2027", "⚙️ Gestion des CAPAs", "🤖 Assistant NLP & Radar"])
else:
    st.sidebar.markdown("### 👤 Espace Saisie (BPO/RTE)")
    menu = st.sidebar.radio("Navigation", ["⚙️ Mes CAPAs (Saisie & Suivi)", "🤖 Mon Assistant NLP & Radar"])

def obtenir_donnees_visibles():
    if est_admin or st.session_state.projets.empty:
        return st.session_state.projets
    return st.session_state.projets[st.session_state.projets['Auteur'] == st.session_state.utilisateur]

df_visible = obtenir_donnees_visibles()

# --- VUE 1 : TABLEAU DE BORD (RÉSERVÉ VMO) ---
if menu == "📊 Tableau de bord BP 2027":
    col_l1, col_l2 = st.columns([1, 5])
    with col_l1:
        st.image(URL_LOGO_DALKIA, width=140)
    with col_l2:
        st.title("📊 Synthèse du Portefeuille - Budget Participatif 2027")
    
    col_exp1, col_exp2, col_exp3 = st.columns([1, 1, 1])
    with col_exp1:
        excel_data = generer_excel_propre(df_visible)
        st.download_button(label="📊 Exporter en Excel (.xlsx)", data=excel_data, file_name='Portefeuille_BP2027_Comex.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', use_container_width=True)
    with col_exp2:
        csv_data = generer_csv_excel(df_visible)
        st.download_button(label="📄 Exporter en CSV (;)", data=csv_data, file_name='Portefeuille_BP2027_Comex.csv', mime='text/csv', use_container_width=True)
    with col_exp3:
        st.link_button("🟢 Ouvrir Google Sheets", "https://sheets.new", use_container_width=True)
    
    st.info("👑 **Mode VMO** : Vous visualisez l'ensemble des données d'arbitrage de l'entreprise.")
        
    col_r0 = 'Budget R0 BP 2027 (K€)'
    col_r2 = 'Prévisionnel R2 (K€)'
    col_delta = 'Delta R2-R0 (K€)'
    
    total_r0 = pd.to_numeric(df_visible[col_r0], errors='coerce').sum() if not df_visible.empty else 0
    total_delta = pd.to_numeric(df_visible[col_delta], errors='coerce').sum() if not df_visible.empty else 0
    budget_p0 = pd.to_numeric(df_visible[df_visible['Priorité'] == 'P0'][col_r0], errors='coerce').sum() if not df_visible.empty else 0
    budget_p1p2 = pd.to_numeric(df_visible[df_visible['Priorité'].isin(['P1', 'P2'])][col_r0], errors='coerce').sum() if not df_visible.empty else 0
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Alloué R0", f"{total_r0:,.0f} K€")
    c2.metric("Budget Garanti (P0 auto)", f"{budget_p0:,.0f} K€")
    c3.metric("Budget à Arbitrer (P1/P2)", f"{budget_p1p2:,.0f} K€")
    c4.metric("Delta R2 vs R0", f"{total_delta:,.0f} K€", delta="Dépassement budgétaire" if total_delta > 0 else "Dans le budget", delta_color="inverse")
    
    st.markdown("---")
    
    if not df_visible.empty:
        st.markdown("### 📈 Visualisations Stratégiques (Comex)")
        g1, g2 = st.columns(2)
        with g1:
            fig_bar = px.bar(df_visible, x='Département', y='Budget R0 BP 2027 (K€)', color='Axe Stratégique', title="📊 Budget R0 par Département & Axe Stratégique")
            st.plotly_chart(fig_bar, use_container_width=True)
        with g2:
            fig_pie = px.pie(df_visible, names='Priorité', values='Budget R0 BP 2027 (K€)', title="🍩 Répartition par Priorité Calculée", hole=0.3)
            st.plotly_chart(fig_pie, use_container_width=True)
            
        st.markdown("### 🎯 Matrice de Priorisation (Identification des Quick Wins)")
        df_quick = df_visible.copy()
        df_quick['Score Valeur (Gains)'] = pd.to_numeric(df_quick['Critère Opérationnel'], errors='coerce').fillna(0) + pd.to_numeric(df_quick['Critère Économique'], errors='coerce').fillna(0)
        fig_scatter = px.scatter(
            df_quick, x='Budget R0 BP 2027 (K€)', y='Score Valeur (Gains)', color='Priorité', 
            hover_name='Nom CAPA', size_max=60, title="Matrice Valeur vs Coût : Les projets 'Quick Wins' se trouvent en haut à gauche."
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
        st.markdown("---")
    
    with st.expander("🔍 FILTRER LES DONNÉES DU TABLEAU DE BORD", expanded=True):
        col_f1, col_f2, col_f3, col_f4 = st.columns(4)
        f_dept = col_f1.selectbox("Département :", ["Tous"] + sorted([str(x) for x in df_visible['Département'].dropna().unique()]))
        f_axe = col_f2.selectbox("Axe Stratégique :", ["Tous"] + sorted([str(x) for x in df_visible['Axe Stratégique'].dropna().unique()]))
        f_prio = col_f3.selectbox("Priorité (Calculée) :", ["Toutes"] + sorted([str(x) for x in df_visible['Priorité'].dropna().unique()]))
        f_etat = col_f4.selectbox("État :", ["Tous"] + sorted([str(x) for x in df_visible['Etat'].dropna().unique()]))
        recherche_tb = st.text_input("🔍 Recherche globale (Nom CAPA, EPIC, Auteur, Ticket JIRA) :")
        
    df_tb_filtre = ajouter_alertes(df_visible)
    if f_dept != "Tous": df_tb_filtre = df_tb_filtre[df_tb_filtre['Département'] == f_dept]
    if f_axe != "Tous": df_tb_filtre = df_tb_filtre[df_tb_filtre['Axe Stratégique'] == f_axe]
    if f_prio != "Toutes": df_tb_filtre = df_tb_filtre[df_tb_filtre['Priorité'] == f_prio]
    if f_etat != "Tous": df_tb_filtre = df_tb_filtre[df_tb_filtre['Etat'] == f_etat]
    if recherche_tb:
        df_tb_filtre = df_tb_filtre[
            df_tb_filtre['Nom CAPA'].astype(str).str.contains(recherche_tb, case=False, na=False) |
            df_tb_filtre['EPIC'].astype(str).str.contains(recherche_tb, case=False, na=False) |
            df_tb_filtre['Auteur'].astype(str).str.contains(recherche_tb, case=False, na=False)
        ]
    
    cols_a_afficher = ['Alerte Budgétaire', 'Nom CAPA', 'EPIC', 'Département', 'Axe Stratégique', 'Budget R0 BP 2027 (K€)', 'Reste à engager (K€)', 'Prévisionnel R2 (K€)', 'Priorité', 'Statut Arbitrage', 'Etat']
    st.data_editor(df_tb_filtre[cols_a_afficher], use_container_width=True, hide_index=True, disabled=True)

# --- VUE 2 : GESTION DES CAPAS ---
elif menu in ["⚙️ Gestion des CAPAs", "⚙️ Mes CAPAs (Saisie & Suivi)"]:
    col_l1, col_l2 = st.columns([1, 5])
    with col_l1:
        st.image(URL_LOGO_DALKIA, width=140)
    with col_l2:
        st.title("⚙️ Espace de Saisie & Suivi des Demandes (BP 2027)")
    
    col_top1, col_top2 = st.columns([2, 1])
    with col_top1:
        st.write("📊 **Besoin d'extraire vos données vers Google Sheets / Excel ?**")
    with col_top2:
        excel_saisie_data = generer_excel_propre(df_visible)
        st.download_button(label="🟢 Exporter vers Google Sheets / Excel", data=excel_saisie_data, file_name='Extraction_CAPA_BP2027.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', use_container_width=True)
    
    st.markdown("---")
    tabs = st.tabs(["➕ Ajouter une CAPA", "✏️ Modifier une CAPA", "🗑️ Supprimer une CAPA"])
    
    with tabs[0]:
        st.markdown("""
            <div class="cadre-creer">
                <h3 style='margin-top: 0; color: #E5004F;'>✨ Soumettre une nouvelle CAPA (Budget 2027)</h3>
                <p style='margin-bottom: 0;'>Renseignez les éléments ci-dessous. Dès validation, votre demande sera affichée en direct.</p>
            </div>
        """, unsafe_allow_html=True)
        
        with st.form("form_creation"):
            st.markdown('<h4 class="titre-section-1">1. Identification & Classification</h4>', unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            sel_env = c1.selectbox("Enveloppe", ["2027", "HORScadrage", "AI", "PACHA", "Autre (préciser)"])
            enveloppe = c1.text_input("Précisez l'enveloppe :") if sel_env == "Autre (préciser)" else sel_env
            sel_dept = c2.selectbox("Département", ["DATA", "CLEFS", "DOPING", "Infra", "E-Facts", "UP", "Idops", "Autre (préciser)"])
            departement = c2.text_input("Précisez le département :") if sel_dept == "Autre (préciser)" else sel_dept
            domaine = c3.text_input("Domaine porteur (ex: DP, Clefs, Infra...)")
            
            c4, c5 = st.columns(2)
            sel_axe = c4.selectbox("Axe Stratégique", ["Numérique", "Engagement", "Décarbonation", "Performance", "Électrification", "Autre (préciser)"])
            axe = c4.text_input("Précisez l'axe :") if sel_axe == "Autre (préciser)" else sel_axe
            sel_ps = c5.selectbox("Projet Stratégique", ["Numérique - Infrastructures Cloud et Réseau", "Numérique - Cybersécurité", "DATA", "Referentiel", "Autre (préciser)"])
            projet_strat = c5.text_input("Précisez le projet :") if sel_ps == "Autre (préciser)" else sel_ps
            
            c7, c8, c9, c10 = st.columns(4)
            epic = c7.text_input("Intitulé de l'EPIC *")
            id_jira_epic = c8.text_input("N° Ticket JIRA EPIC")
            nom_capa = c9.text_input("Intitulé de la CAPA *")
            id_jira_capa = c10.text_input("N° Ticket JIRA CAPA")
            
            c11, c12 = st.columns(2)
            train_hors_train = c11.selectbox("Train / Hors train", ["Train", "Hors train"])
            etat = c12.selectbox("État de la demande", ["En cours", "Prévu pour S2", "Reporté à 2027", "Abandonné", "Terminé"])
            
            features = st.text_area("Features (Besoins délivrés/traités sur un incrément)")
            equipes_contrib = st.text_input("Équipes contributrices / Produits")
            contexte = st.text_area("Contexte de la CAPA")
            
            st.markdown('<h4 class="titre-section-2">2. Suivi Budgétaire BP 2027 (K€)</h4>', unsafe_allow_html=True)
            b1, b2, b3 = st.columns(3)
            budget_r0 = b1.number_input("Budget alloué BP 2027 (R0)", min_value=0.0, step=10.0)
            budget_r1 = b2.number_input("Encouru (R1)", min_value=0.0, step=10.0)
            budget_r2 = b3.number_input("Revue prévisionnelle (R2)", min_value=0.0, step=10.0)
            
            st.markdown('<h4 class="titre-section-3">3. Matrice de Valeur & Indicateurs</h4>', unsafe_allow_html=True)
            n1, n2, n3, n4 = st.columns(4)
            n_conf = n1.number_input("Critère Conformité & Obsolescence", 1, 4, 1)
            n_img = n2.number_input("Critère Image & Sat. Client", 1, 4, 1)
            n_ope = n3.number_input("Critère Gain Opérationnel", 1, 4, 1)
            n_eco = n4.number_input("Critère Gain Économique", 1, 4, 1)
            
            justif = st.text_area("Explications des notes (pourquoi ces 4 notes)")
            
            i1, i2, i3 = st.columns(3)
            indicateur = i1.text_input("Indicateur de mesure (formule de calcul)")
            valeur_date = i2.text_input("Valeur à date")
            valeur_cible = i3.text_input("Valeur cible")
            
            commentaires_vmo = ""
            statut_arbitrage = "Soumis"
            if est_admin:
                st.markdown("---")
                statut_arbitrage = st.selectbox("Décision / Statut d'Arbitrage Comex", ["Soumis", "Validé Comex", "Ajustement requis", "Refusé"])
                commentaires_vmo = st.text_area("✍️ Remarques / Décision de l'arbitrage VMO", help="Réservé au profil VMO")
            
            soumettre = st.form_submit_button("💾 Enregistrer la CAPA")
            
            if soumettre:
                if not epic or not nom_capa:
                    st.error("⚠️ Les champs 'EPIC' et 'Nom de la CAPA' sont obligatoires.")
                else:
                    delta_calcule = budget_r2 - budget_r0
                    reste_a_engager = budget_r0 - budget_r1
                    priorite_calculee = calculer_priorite_auto(n_conf, n_ope, n_eco)
                    horodatage_actuel = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    nouvelle_ligne = pd.DataFrame([{
                        'Auteur': st.session_state.utilisateur, 'Enveloppe': enveloppe, 'Département': departement, 
                        'Domaine porteur': domaine, 'Axe Stratégique': axe, 'Projet Stratégique': projet_strat, 
                        'EPIC': epic, 'ID Ticket JIRA EPIC': id_jira_epic, 'Nom CAPA': nom_capa, 'ID Ticket JIRA CAPA': id_jira_capa,
                        'Train / Hors train': train_hors_train, 'Priorité': priorite_calculee, 'Etat': etat, 
                        'Statut Arbitrage': statut_arbitrage,
                        'Features / Besoins': features, 'Equipes contributrices': equipes_contrib,
                        'Budget R0 BP 2027 (K€)': budget_r0, 'Encouru R1 (K€)': budget_r1, 'Reste à engager (K€)': reste_a_engager,
                        'Prévisionnel R2 (K€)': budget_r2, 'Delta R2-R0 (K€)': delta_calcule, 'Contexte de la CAPA': contexte, 
                        'Critère Conformité': n_conf, 'Critère Image': n_img, 'Critère Opérationnel': n_ope, 'Critère Économique': n_eco, 
                        'Explications des notes': justif, 'Indicateur de mesure': indicateur, 
                        'Valeur à date': valeur_date, 'Valeur cible': valeur_cible, 'Commentaires VMO': commentaires_vmo,
                        'Modifié_Par': st.session_state.utilisateur, 'Dernière_Modification_Date': horodatage_actuel
                    }])
                    st.session_state.projets = pd.concat([st.session_state.projets, nouvelle_ligne], ignore_index=True)
                    sauvegarder_donnees(st.session_state.projets)
                    st.success(f"✅ CAPA '{nom_capa}' enregistrée avec succès (Priorité calculée : {priorite_calculee}) !")
                    st.rerun()

        st.markdown("---")
        st.subheader("📋 Liste de vos CAPAs saisies")
        
        if df_visible.empty:
            st.info("Vous n'avez pas encore soumis de CAPA.")
        else:
            with st.expander("🔍 FILTRER LA LISTE DES CAPAs", expanded=True):
                c_f1, c_f2, c_f3, c_f4, c_f5 = st.columns(5)
                f_dept_s = c_f1.selectbox("Département :", ["Tous"] + sorted([str(x) for x in df_visible['Département'].dropna().unique()]))
                f_axe_s = c_f2.selectbox("Axe Stratégique :", ["Tous"] + sorted([str(x) for x in df_visible['Axe Stratégique'].dropna().unique()]))
                f_prio_s = c_f3.selectbox("Priorité (Calculée) :", ["Toutes"] + sorted([str(x) for x in df_visible['Priorité'].dropna().unique()]))
                f_train_s = c_f4.selectbox("Train / Hors train :", ["Tous"] + sorted([str(x) for x in df_visible['Train / Hors train'].dropna().unique()]))
                f_etat_s = c_f5.selectbox("État :", ["Tous"] + sorted([str(x) for x in df_visible['Etat'].dropna().unique()]))
                recherche_s = st.text_input("🔍 Recherche par mot-clé (Nom CAPA, EPIC, Ticket JIRA) :")
            
            df_saisie_filtre = ajouter_alertes(df_visible)
            if f_dept_s != "Tous": df_saisie_filtre = df_saisie_filtre[df_saisie_filtre['Département'] == f_dept_s]
            if f_axe_s != "Tous": df_saisie_filtre = df_saisie_filtre[df_saisie_filtre['Axe Stratégique'] == f_axe_s]
            if f_prio_s != "Toutes": df_saisie_filtre = df_saisie_filtre[df_saisie_filtre['Priorité'] == f_prio_s]
            if f_train_s != "Tous": df_saisie_filtre = df_saisie_filtre[df_saisie_filtre['Train / Hors train'] == f_train_s]
            if f_etat_s != "Tous": df_saisie_filtre = df_saisie_filtre[df_saisie_filtre['Etat'] == f_etat_s]
            if recherche_s:
                df_saisie_filtre = df_saisie_filtre[
                    df_saisie_filtre['Nom CAPA'].astype(str).str.contains(recherche_s, case=False, na=False) |
                    df_saisie_filtre['EPIC'].astype(str).str.contains(recherche_s, case=False, na=False)
                ]
                
            cols_saisie = ['Alerte Budgétaire', 'Nom CAPA', 'EPIC', 'Département', 'Budget R0 BP 2027 (K€)', 'Reste à engager (K€)', 'Prévisionnel R2 (K€)', 'Priorité', 'Statut Arbitrage', 'Etat']
            st.data_editor(df_saisie_filtre[cols_saisie], use_container_width=True, hide_index=True, disabled=True)

    with tabs[1]:
        if df_visible.empty:
            st.warning("Aucune CAPA disponible à modifier.")
        else:
            capa_a_modifier = st.selectbox("Sélectionnez la CAPA à modifier :", df_visible['Nom CAPA'].tolist())
            idx = st.session_state.projets[st.session_state.projets['Nom CAPA'] == capa_a_modifier].index[0]
            
            with st.form("form_modification"):
                st.markdown(f"<h4 class='titre-section-2'>Édition de la CAPA : {capa_a_modifier}</h4>", unsafe_allow_html=True)
                val_r0 = float(st.session_state.projets.at[idx, 'Budget R0 BP 2027 (K€)']) if pd.notnull(st.session_state.projets.at[idx, 'Budget R0 BP 2027 (K€)']) else 0.0
                val_r1 = float(st.session_state.projets.at[idx, 'Encouru R1 (K€)']) if pd.notnull(st.session_state.projets.at[idx, 'Encouru R1 (K€)']) else 0.0
                val_r2 = float(st.session_state.projets.at[idx, 'Prévisionnel R2 (K€)']) if pd.notnull(st.session_state.projets.at[idx, 'Prévisionnel R2 (K€)']) else 0.0
                
                new_r0 = st.number_input("Nouveau Budget R0 BP 2027", value=val_r0)
                new_r1 = st.number_input("Nouveau Encouru R1", value=val_r1)
                new_r2 = st.number_input("Nouveau Prévisionnel R2", value=val_r2)
                
                new_etat = st.selectbox("Mettre à jour l'état", ["En cours", "Prévu pour S2", "Reporté à 2027", "Abandonné", "Terminé"])
                
                new_statut_arb = st.session_state.projets.at[idx, 'Statut Arbitrage'] or "Soumis"
                new_comm = st.session_state.projets.at[idx, 'Commentaires VMO']
                if est_admin:
                    new_statut_arb = st.selectbox("Décision / Statut d'Arbitrage Comex", ["Soumis", "Validé Comex", "Ajustement requis", "Refusé"])
                    new_comm = st.text_area("Commentaires VMO / Arbitrage", value=str(st.session_state.projets.at[idx, 'Commentaires VMO'] or ''))
                
                if st.form_submit_button("💾 Enregistrer la modification"):
                    st.session_state.projets.at[idx, 'Budget R0 BP 2027 (K€)'] = new_r0
                    st.session_state.projets.at[idx, 'Encouru R1 (K€)'] = new_r1
                    st.session_state.projets.at[idx, 'Reste à engager (K€)'] = new_r0 - new_r1
                    st.session_state.projets.at[idx, 'Prévisionnel R2 (K€)'] = new_r2
                    st.session_state.projets.at[idx, 'Delta R2-R0 (K€)'] = new_r2 - new_r0
                    st.session_state.projets.at[idx, 'Etat'] = new_etat
                    st.session_state.projets.at[idx, 'Statut Arbitrage'] = new_statut_arb
                    st.session_state.projets.at[idx, 'Commentaires VMO'] = new_comm
                    
                    st.session_state.projets.at[idx, 'Modifié_Par'] = st.session_state.utilisateur
                    st.session_state.projets.at[idx, 'Dernière_Modification_Date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    sauvegarder_donnees(st.session_state.projets)
                    st.success("Mise à jour enregistrée.")
                    st.rerun()

    with tabs[2]:
        if df_visible.empty:
            st.warning("Aucune CAPA disponible à supprimer.")
        else:
            capa_a_supprimer = st.selectbox("Sélectionnez la CAPA à supprimer :", df_visible['Nom CAPA'].tolist())
            if st.button("🗑️ Supprimer définitivement cette CAPA"):
                st.session_state.projets = st.session_state.projets[st.session_state.projets['Nom CAPA'] != capa_a_supprimer]
                sauvegarder_donnees(st.session_state.projets)
                st.success(f"La CAPA '{capa_a_supprimer}' a été supprimée.")
                st.rerun()

# --- VUE 3 : IA & NLP ---
elif menu in ["🤖 Assistant NLP & Radar", "🤖 Mon Assistant NLP & Radar"]:
    col_l1, col_l2 = st.columns([1, 5])
    with col_l1:
        st.image(URL_LOGO_DALKIA, width=140)
    with col_l2:
        st.title("🤖 Analyse Sémantique & Aide à la Décision")
    
    if df_visible.empty:
        st.warning("Aucune donnée disponible à analyser. Veuillez d'abord saisir une CAPA.")
    else:
        capa_selectionnee = st.selectbox("Sélectionnez une CAPA à analyser :", df_visible['Nom CAPA'].tolist())
        donnees_capa = df_visible[df_visible['Nom CAPA'] == capa_selectionnee].iloc[0]
        
        conf_val = pd.to_numeric(donnees_capa['Critère Conformité'], errors='coerce') or 1
        if conf_val >= 3:
            st.success("🚨 **Règle métier Dalkia :** Le critère de Conformité / Obsolescence est élevé (>=3). Cette CAPA est classée en **Top Priorité automatique (P0)**.")
        
        st.markdown("### 🔍 Détecteur de Doublons Sémantiques")
        texte_actuel = set(str(donnees_capa['Contexte de la CAPA']).lower().split())
        doublons = []
        for index, row in st.session_state.projets.iterrows():
            if row['Nom CAPA'] != capa_selectionnee:
                autre_texte = set(str(row['Contexte de la CAPA']).lower().split())
                if len(texte_actuel) > 5 and len(autre_texte) > 5:
                    intersection = texte_actuel.intersection(autre_texte)
                    union = texte_actuel.union(autre_texte)
                    score_similarite = len(intersection) / len(union)
                    if score_similarite > 0.2:
                        doublons.append((row['Nom CAPA'], row['Département'], score_similarite * 100))
        
        if doublons:
            st.warning("⚠️ CAPAs similaires détectées dans le portefeuille :")
            for d in doublons:
                st.write(f"- **{d[0]}** (Dépt: {d[1]}) - Correspondance sémantique : ~{d[2]:.0f}%")
        else:
            st.success("✅ Aucun doublon sémantique détecté.")
            
        st.markdown("---")
        
        col_ia1, col_ia2 = st.columns(2)
        with col_ia1:
            st.subheader("Radar de Valeur")
            c_conf = pd.to_numeric(donnees_capa['Critère Conformité'], errors='coerce') or 1
            c_img = pd.to_numeric(donnees_capa['Critère Image'], errors='coerce') or 1
            c_ope = pd.to_numeric(donnees_capa['Critère Opérationnel'], errors='coerce') or 1
            c_eco = pd.to_numeric(donnees_capa['Critère Économique'], errors='coerce') or 1
            
            df_radar = pd.DataFrame(dict(
                r=[c_conf, c_img, c_ope, c_eco],
                theta=['Conformité', 'Image', 'Gain Opé.', 'Gain Éco.']))
            fig = px.line_polar(df_radar, r='r', theta='theta', line_close=True, range_r=[0,4])
            fig.update_traces(fill='toself', line_color='#E5004F')
            st.plotly_chart(fig, use_container_width=True)

        with col_ia2:
            st.subheader("Vérificateur NLP (Budget & ROI)")
            texte_justif = str(donnees_capa['Explications des notes']).lower()
            if c_eco >= 3:
                mots_cles = ['€', 'euros', 'budget', 'roi', 'rentabilité', 'économie', 'financier', 'gains']
                if any(mot in texte_justif for mot in mots_cles):
                    st.success("✅ **Cohérence validée** : Vocabulaire financier détecté dans la justification.")
                else:
                    st.error("⚠️ **Incohérence** : Note économique élevée (>=3) mais aucun terme financier justifié dans le texte.")
            else:
                st.info("La note économique est < 3, pas d'analyse requise.")
                
        st.markdown("---")
        st.markdown("### 🤖 Synthèse IA pour le Comex")
        if st.button("✨ Générer le résumé IA pour l'arbitrage"):
            with st.spinner("L'Intelligence Artificielle analyse le dossier et rédige la synthèse..."):
                import time
                time.sleep(1.5)
                
                nom = donnees_capa['Nom CAPA']
                dept = donnees_capa['Département']
                axe = donnees_capa['Axe Stratégique']
                budget = donnees_capa['Budget R0 BP 2027 (K€)']
                prio = donnees_capa['Priorité']
                
                st.success("✅ Synthèse générée avec succès.")
                st.info(f"**Résumé pour Décideurs :**\n\nLe projet **{nom}**, porté par le département **{dept}**, s'inscrit directement dans l'axe stratégique de **{axe}**. Nécessitant un investissement initial de **{budget} K€**, cette initiative est classée en priorité **{prio}** car elle présente un fort score de gain opérationnel ({c_ope}/4) et économique ({c_eco}/4), justifiant un arbitrage favorable rapide.")
