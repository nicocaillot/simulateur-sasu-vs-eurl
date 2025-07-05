import streamlit as st
import matplotlib.pyplot as plt
from fpdf import FPDF
from io import BytesIO

st.set_page_config(page_title="Simulateur SASU vs EURL", page_icon="📊", layout="centered")
st.title("🧮 Simulateur SASU vs EURL avec dividendes")

# === Sélecteur périodicité ===
frequence = st.radio("🗓️ Voir les résultats :", ["Annuel", "Mensuel"])
facteur = 1 if frequence == "Annuel" else 1 / 12

# === Entrées utilisateur ===
ca = st.number_input("💰 Chiffre d'affaires", value=80000) * facteur
charges = st.number_input("💸 Charges hors rémunération", value=20000) * facteur
remu = st.number_input("👨‍💼 Rémunération du dirigeant", value=30000) * facteur
auto_dividendes = st.checkbox("📌 SASU : percevoir tous les bénéfices comme dividendes")
eurl_avec_is = st.checkbox("🏛️ EURL soumise à l'IS (option fiscale)")

# === Constantes fiscales ===
taux_cot_sasu = 0.75
taux_cot_eurl = 0.45
taux_flat_tax = 0.30
taux_ir_eurl = 0.11  # utilisé si EURL sans IS

def calcul_is(resultat):
    if resultat <= 0:
        return 0
    if resultat <= 42500:
        return resultat * 0.15
    else:
        return 42500 * 0.15 + (resultat - 42500) * 0.25

# === SASU ===
resultat_sasu = ca - charges - remu
cot_sasu = remu * taux_cot_sasu
is_sasu = calcul_is(resultat_sasu)
revenu_net_sasu = remu - cot_sasu

if auto_dividendes:
    dividendes = max(0, resultat_sasu - is_sasu)
else:
    dividendes = st.number_input("📈 Dividendes SASU (€)", value=5000 * facteur)

revenu_dividende_net = dividendes * (1 - taux_flat_tax)
total_net_sasu = revenu_net_sasu + revenu_dividende_net

# === EURL ===
cot_eurl = remu * taux_cot_eurl
resultat_eurl = ca - charges - remu
revenu_net_eurl = remu - cot_eurl

if eurl_avec_is:
    is_eurl = calcul_is(resultat_eurl)
    revenu_total_eurl = revenu_net_eurl  # pas d'IR sur revenu pro
    revenu_div_eurl = max(0, resultat_eurl - is_eurl) * (1 - taux_flat_tax)
    total_net_eurl = revenu_net_eurl + revenu_div_eurl
else:
    ir_eurl = max(0, resultat_eurl * taux_ir_eurl)
    total_net_eurl = revenu_net_eurl  # déjà net d’IR via taux simplifié

# === Affichage résultats ===
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 SASU")
    st.write(f"Résultat : **{resultat_sasu:.0f} €**")
    st.write(f"IS (15 % / 25 %) : **{is_sasu:.0f} €**")
    st.write(f"Cotisations sociales : **{cot_sasu:.0f} €**")
    st.write(f"Rémunération nette (avant IR perso) : **{revenu_net_sasu:.0f} €**")
    st.write(f"Dividendes nets (flat tax) : **{revenu_dividende_net:.0f} €**")
    st.write(f"🟢 Revenu net {frequence.lower()} : **{total_net_sasu:.0f} €**")

with col2:
    st.subheader("📊 EURL")
    st.write(f"Résultat : **{resultat_eurl:.0f} €**")
    st.write(f"Cotisations sociales : **{cot_eurl:.0f} €**")
    if eurl_avec_is:
        st.write(f"IS (15 % / 25 %) : **{is_eurl:.0f} €**")
        st.write(f"Dividendes nets (flat tax) : **{revenu_div_eurl:.0f} €**")
    else:
        st.write(f"IR estimé (11 %) : **{ir_eurl:.0f} €**")
    st.write(f"🟢 Revenu net {frequence.lower()} : **{total_net_eurl:.0f} €**")

# === Graphique comparatif ===
st.markdown("---")
fig, ax = plt.subplots()
ax.bar(["SASU", "EURL"], [total_net_sasu, total_net_eurl], color=["#4caf50", "#2196f3"])
ax.set_ylabel(f"Revenu net {frequence.lower()} (€)")
ax.set_title("Comparatif SASU vs EURL")
st.pyplot(fig)

# === Comparatif final ===
diff = total_net_sasu - total_net_eurl
if diff > 0:
    st.success(f"✅ SASU plus avantageuse de **{diff:.0f} €** par {frequence.lower()}")
elif diff < 0:
    st.error(f"❌ EURL plus avantageuse de **{-diff:.0f} €** par {frequence.lower()}")
else:
    st.info("⚖️ Égalité parfaite entre SASU et EURL.")

# === Export PDF (optionnel à compléter si besoin) ===
if st.button("📄 Export PDF (à ajouter bientôt)"):
    st.warning("Fonction d'export PDF en cours d'adaptation pour cette version.")