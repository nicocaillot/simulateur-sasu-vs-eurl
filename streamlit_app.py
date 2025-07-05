import streamlit as st
import matplotlib.pyplot as plt
from fpdf import FPDF
from io import BytesIO

st.set_page_config(page_title="Simulateur SASU vs EURL", page_icon="📊", layout="centered")
st.title("🧮 Simulateur SASU vs EURL")

# === Sélecteur annuel / mensuel ===
frequence = st.radio("🗓️ Voir les résultats :", ["Annuel", "Mensuel"])
facteur = 1 if frequence == "Annuel" else 1 / 12

# === Entrée utilisateur ===
ca = st.number_input("💰 Chiffre d'affaires", value=80000) * facteur
charges = st.number_input("💸 Charges hors rémunération", value=20000) * facteur
remu_net = st.number_input("👨‍💼 Rémunération NETTE souhaitée (en main)", value=30000) * facteur

auto_dividendes = st.checkbox("📌 SASU : percevoir tous les bénéfices comme dividendes")
eurl_avec_is = st.checkbox("🏛️ EURL soumise à l'IS (option fiscale)")

# === Constantes fiscales ===
taux_cot_sasu = 0.75
taux_cot_eurl = 0.45
taux_flat_tax = 0.30
taux_ir_eurl = 0.11  # forfaitaire

def calcul_is(resultat):
    if resultat <= 0:
        return 0
    if resultat <= 42500:
        return resultat * 0.15
    else:
        return 42500 * 0.15 + (resultat - 42500) * 0.25

# === Rémunération brute (calculée) ===
remu_brute_sasu = remu_net / (1 - taux_cot_sasu)
remu_brute_eurl = remu_net / (1 - taux_cot_eurl)
cot_sasu = remu_brute_sasu - remu_net
cot_eurl = remu_brute_eurl - remu_net

# === SASU ===
resultat_sasu = ca - charges - remu_brute_sasu
is_sasu = calcul_is(resultat_sasu)
if auto_dividendes:
    dividendes_sasu = max(0, resultat_sasu - is_sasu)
else:
    dividendes_sasu = st.number_input("📈 Dividendes SASU", value=5000 * facteur)
dividendes_net_sasu = dividendes_sasu * (1 - taux_flat_tax)
total_net_sasu = remu_net + dividendes_net_sasu

# === EURL ===
resultat_eurl = ca - charges - remu_brute_eurl
if eurl_avec_is:
    is_eurl = calcul_is(resultat_eurl)
    dividendes_eurl = max(0, resultat_eurl - is_eurl)
    dividendes_net_eurl = dividendes_eurl * (1 - taux_flat_tax)
    total_net_eurl = remu_net + dividendes_net_eurl
else:
    ir_eurl = max(0, resultat_eurl * taux_ir_eurl)
    total_net_eurl = remu_net  # net déjà après IR

# === Affichage résultats ===
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 SASU")
    st.write(f"Rémunération nette choisie : **{remu_net:.0f} €**")
    st.write(f"Rémunération brute requise : **{remu_brute_sasu:.0f} €**")
    st.write(f"Charges sociales (75%) : **{cot_sasu:.0f} €**")
    st.write(f"Résultat société : **{resultat_sasu:.0f} €**")
    st.write(f"IS : **{is_sasu:.0f} €**")
    st.write(f"Dividendes nets : **{dividendes_net_sasu:.0f} €**")
    st.write(f"🟢 Revenu net total : **{total_net_sasu:.0f} €** par {frequence.lower()}")

with col2:
    st.subheader("📊 EURL")
    st.write(f"Rémunération nette choisie : **{remu_net:.0f} €**")
    st.write(f"Rémunération brute requise : **{remu_brute_eurl:.0f} €**")
    st.write(f"Charges sociales (45%) : **{cot_eurl:.0f} €**")
    st.write(f"Résultat société : **{resultat_eurl:.0f} €**")
    if eurl_avec_is:
        st.write(f"IS : **{is_eurl:.0f} €**")
        st.write(f"Dividendes nets : **{dividendes_net_eurl:.0f} €**")
        st.write(f"🟢 Revenu net total : **{total_net_eurl:.0f} €** par {frequence.lower()}")
    else:
        st.write(f"IR estimé (11%) : **{ir_eurl:.0f} €**")
        st.write(f"🟢 Revenu net total : **{total_net_eurl:.0f} €** par {frequence.lower()}")

# === Graphique comparatif ===
st.markdown("---")
fig, ax = plt.subplots()
ax.bar(["SASU", "EURL"], [total_net_sasu, total_net_eurl], color=["#4caf50", "#2196f3"])
ax.set_ylabel(f"Revenu net {frequence.lower()} (€)")
ax.set_title("Comparatif SASU vs EURL")
st.pyplot(fig)

# === Conclusion ===
diff = total_net_sasu - total_net_eurl
if diff > 0:
    st.success(f"✅ SASU plus avantageuse de **{diff:.0f} €** par {frequence.lower()}")
elif diff < 0:
    st.error(f"❌ EURL plus avantageuse de **{-diff:.0f} €** par {frequence.lower()}")
else:
    st.info("⚖️ Égalité parfaite entre SASU et EURL.")

# === Export PDF à compléter si besoin ===
if st.button("📄 Export PDF (à venir)"):
    st.warning("L'export PDF sera mis à jour avec les nouveaux calculs très bientôt.")