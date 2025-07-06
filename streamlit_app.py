import streamlit as st import matplotlib.pyplot as plt

st.set_page_config(page_title="Simulateur SASU vs EURL", page_icon="📊", layout="centered") st.title("🧼 Simulateur SASU vs EURL")

frequence = st.radio("🗓️ Voir les résultats :", ["Annuel", "Mensuel"]) facteur = 1 if frequence == "Annuel" else 1 / 12 mode_saisie = st.radio("💼 Type de rémunération saisie :", ["Nette", "Coût employeur"])

taux_sasu = 0.82 taux_eurl = 0.66 taux_flat_tax = 0.30

ca = st.number_input("💰 Chiffre d'affaires", value=30000) * facteur charges = st.number_input("💸 Charges hors rémunération", value=0) * facteur eurl_avec_is = st.checkbox("🏛️ EURL soumise à l'IS") auto_dividendes = st.checkbox("📌 SASU : percevoir tous les bénéfices comme dividendes")

if mode_saisie == "Nette": remu_net = st.number_input("👤 Rémunération nette souhaitée", value=0) * facteur remu_brute_sasu = remu_net * (1 + taux_sasu) remu_brute_eurl = remu_net * (1 + taux_eurl) else: remu_brute = st.number_input("👤 Rémunération brute souhaitée", value=0) * facteur remu_net = remu_brute / (1 + taux_sasu) remu_brute_sasu = remu_brute remu_brute_eurl = remu_brute

cot_sasu = remu_brute_sasu - remu_net cot_eurl = remu_brute_eurl - remu_net

def calcul_is(resultat): if resultat <= 0: return 0 if resultat <= 42500: return resultat * 0.15 else: return 42500 * 0.15 + (resultat - 42500) * 0.25

cout_sasu = remu_brute_sasu resultat_sasu = ca - charges - cout_sasu is_sasu = calcul_is(resultat_sasu) benefice_net_sasu = resultat_sasu - is_sasu div_sasu = max(0, benefice_net_sasu) if auto_dividendes else st.number_input("📈 Dividendes SASU", value=5000 * facteur) div_net_sasu = div_sasu * (1 - taux_flat_tax) revenu_net_sasu = remu_net + div_net_sasu

cout_eurl = remu_brute_eurl if eurl_avec_is: resultat_eurl = ca - charges - cout_eurl is_eurl = calcul_is(resultat_eurl) benefice_net_eurl = resultat_eurl - is_eurl div_eurl = max(0, benefice_net_eurl) div_eurl = st.number_input("📈 Dividendes EURL", value=div_eurl) div_net_eurl = div_eurl * (1 - taux_flat_tax) revenu_net_eurl = remu_net + div_net_eurl else: resultat_eurl = ca - charges is_eurl = 0 benefice_net_eurl = resultat_eurl div_net_eurl = 0 revenu_net_eurl = remu_net

col1, col2 = st.columns(2)

with col1: with st.container(): st.markdown("<div style='border: 1px solid #cccccc; border-radius: 8px; padding: 16px;'>", unsafe_allow_html=True) st.subheader("📊 SASU") st.markdown("### 💼 Rémunération") st.write(f"Rémunération nette : {remu_net:.0f} €") st.write(f"Charges sociales estimées : {cot_sasu:.0f} € ({taux_sasu*100:.0f} %)") st.write(f"?

