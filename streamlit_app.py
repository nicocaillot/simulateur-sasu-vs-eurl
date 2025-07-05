import streamlit as st
import matplotlib.pyplot as plt
from fpdf import FPDF
from io import BytesIO

st.set_page_config(page_title="Simulateur SASU vs EURL", page_icon="📊", layout="centered")
st.title("🧮 Simulateur SASU vs EURL avec dividendes")

# === Entrée utilisateur ===
ca = st.number_input("💰 Chiffre d'affaires annuel (€)", value=80000, step=1000)
charges = st.number_input("💸 Charges annuelles hors rémunération (€)", value=20000, step=1000)
remu = st.number_input("👨‍💼 Rémunération du dirigeant (€)", value=30000, step=1000)
auto_dividendes = st.checkbox("📌 Percevoir tous les bénéfices comme dividendes (SASU)")

# === Constantes fiscales ===
taux_cot_sasu = 0.75
taux_cot_eurl = 0.45
taux_flat_tax = 0.30
taux_ir_eurl = 0.11  # approximation IR pour EURL

# === Fonctions fiscales ===
def calcul_is(resultat):
    if resultat <= 0:
        return 0
    if resultat <= 42500:
        return resultat * 0.15
    else:
        return 42500 * 0.15 + (resultat - 42500) * 0.25

# === Calcul SASU ===
resultat_sasu = ca - charges - remu
cot_sasu = remu * taux_cot_sasu
is_sasu = calcul_is(resultat_sasu)
revenu_net_sasu = remu - cot_sasu  # avant IR personnel

if auto_dividendes:
    dividendes = max(0, resultat_sasu - is_sasu)
else:
    dividendes = st.number_input("📈 Dividendes (SASU uniquement) (€)", value=5000, step=500)

revenu_dividende_net = dividendes * (1 - taux_flat_tax)
total_net_sasu = revenu_net_sasu + revenu_dividende_net

# === Calcul EURL ===
cot_eurl = remu * taux_cot_eurl
resultat_eurl = ca - charges - remu
ir_eurl = max(0, resultat_eurl * taux_ir_eurl)
revenu_net_eurl = remu - cot_eurl
total_net_eurl = revenu_net_eurl  # après IR société

# === Affichage résultats ===
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 SASU")
    st.write(f"Résultat société : **{resultat_sasu:.0f} €**")
    st.write(f"IS (15 % puis 25 %) : **{is_sasu:.0f} €**")
    st.write(f"Cotisations sociales : **{cot_sasu:.0f} €**")
    st.write(f"Rémunération nette (avant IR personnel) : **{revenu_net_sasu:.0f} €**")
    st.write(f"Dividendes nets (après flat tax) : **{revenu_dividende_net:.0f} €**")
    st.write(f"🟢 Revenu total net SASU : **{total_net_sasu:.0f} €**")

with col2:
    st.subheader("📊 EURL")
    st.write(f"Résultat société : **{resultat_eurl:.0f} €**")
    st.write(f"IR estimé (11 %) : **{ir_eurl:.0f} €**")
    st.write(f"Cotisations sociales : **{cot_eurl:.0f} €**")
    st.write(f"🟢 Revenu total net EURL (après IR) : **{total_net_eurl:.0f} €**")

# === Graphique comparatif ===
st.markdown("---")
fig, ax = plt.subplots()
ax.bar(["SASU", "EURL"], [total_net_sasu, total_net_eurl], color=["#4caf50", "#2196f3"])
ax.set_ylabel("Revenu net (€)")
ax.set_title("Comparatif des revenus nets")
st.pyplot(fig)

# === Conclusion comparative ===
diff = total_net_sasu - total_net_eurl
if diff > 0:
    st.success(f"✅ SASU est plus avantageuse de **{diff:.0f} €**")
elif diff < 0:
    st.error(f"❌ EURL est plus avantageuse de **{-diff:.0f} €**")
else:
    st.info("⚖️ Égalité parfaite entre SASU et EURL.")

# === Export PDF ===
st.markdown("---")
if st.button("📄 Exporter en PDF"):

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Simulation SASU vs EURL", ln=1)

    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Chiffre d'affaires : {ca:.0f} €", ln=1)
    pdf.cell(0, 10, f"Charges : {charges:.0f} €", ln=1)
    pdf.cell(0, 10, f"Rémunération : {remu:.0f} €", ln=1)
    pdf.ln(5)

    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "SASU :", ln=1)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Résultat société : {resultat_sasu:.0f} €", ln=1)
    pdf.cell(0, 10, f"IS calculé : {is_sasu:.0f} €", ln=1)
    pdf.cell(0, 10, f"Cotisations : {cot_sasu:.0f} €", ln=1)
    pdf.cell(0, 10, f"Rémunération nette (avant IR perso) : {revenu_net_sasu:.0f} €", ln=1)
    pdf.cell(0, 10, f"Dividendes nets (après flat tax) : {revenu_dividende_net:.0f} €", ln=1)
    pdf.cell(0, 10, f"Revenu total net SASU : {total_net_sasu:.0f} €", ln=1)

    pdf.ln(5)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "EURL :", ln=1)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Résultat société : {resultat_eurl:.0f} €", ln=1)
    pdf.cell(0, 10, f"IR estimé (11 %) : {ir_eurl:.0f} €", ln=1)
    pdf.cell(0, 10, f"Cotisations : {cot_eurl:.0f} €", ln=1)
    pdf.cell(0, 10, f"Revenu net après IR : {total_net_eurl:.0f} €", ln=1)

    pdf.ln(5)
    if diff != 0:
        meilleure = "SASU" if diff > 0 else "EURL"
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, f"{meilleure} plus avantageuse de {abs(diff):.0f} €", ln=1)

    buffer = BytesIO()
    pdf.output(buffer)
    st.download_button(label="📥 Télécharger le PDF", data=buffer.getvalue(), file_name="simulation-sasu-vs-eurl.pdf", mime="application/pdf")