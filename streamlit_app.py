import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(page_title="Simulateur SASU vs EURL", page_icon="📊", layout="centered")
st.title("🧮 Simulateur SASU vs EURL")

# === Période
frequence = st.radio("🗓️ Voir les résultats :", ["Annuel", "Mensuel"])
facteur = 1 if frequence == "Annuel" else 1 / 12

# === Mode de saisie
mode_saisie = st.radio("💼 Type de rémunération saisie :", ["Nette", "Brute"])

# === Taux de charges globales (réalistes)
taux_sasu = 0.82  # 82% du net
taux_eurl = 0.66
taux_flat_tax = 0.30

# === Entrées utilisateur
ca = st.number_input("💰 Chiffre d'affaires", value=80000) * facteur
charges = st.number_input("💸 Charges hors rémunération", value=20000) * facteur
eurl_avec_is = st.checkbox("🏛️ EURL soumise à l'IS")
auto_dividendes = st.checkbox("📌 SASU : percevoir tous les bénéfices comme dividendes")

# === Rémunération
if mode_saisie == "Nette":
    remu_net = st.number_input("👤 Rémunération nette souhaitée", value=13500) * facteur
    remu_brute_sasu = remu_net * (1 + taux_sasu)
    remu_brute_eurl = remu_net * (1 + taux_eurl)
else:
    remu_brute = st.number_input("👤 Rémunération brute souhaitée", value=25000) * facteur
    remu_net = remu_brute / (1 + taux_sasu) if taux_sasu != 0 else remu_brute
    remu_brute_sasu = remu_brute
    remu_brute_eurl = remu_brute

cot_sasu = remu_brute_sasu - remu_net
cot_eurl = remu_brute_eurl - remu_net

# === IS progressif
def calcul_is(resultat):
    if resultat <= 0:
        return 0
    if resultat <= 42500:
        return resultat * 0.15
    else:
        return 42500 * 0.15 + (resultat - 42500) * 0.25

# === SASU
cout_sasu = remu_brute_sasu
resultat_sasu = ca - charges - cout_sasu
is_sasu = calcul_is(resultat_sasu)
div_sasu = max(0, resultat_sasu - is_sasu) if auto_dividendes else st.number_input("📈 Dividendes SASU", value=5000 * facteur)
div_net_sasu = div_sasu * (1 - taux_flat_tax)
revenu_net_sasu = remu_net + div_net_sasu

# === EURL
cout_eurl = remu_brute_eurl
if eurl_avec_is:
    resultat_eurl = ca - charges - cout_eurl
    is_eurl = calcul_is(resultat_eurl)
    div_net_eurl = max(0, resultat_eurl - is_eurl) * (1 - taux_flat_tax)
    revenu_net_eurl = remu_net + div_net_eurl
else:
    resultat_eurl = ca - charges  # Rémunération NON déductible à l'IR
    is_eurl = 0
    div_net_eurl = 0
    revenu_net_eurl = remu_net

# === Affichage SASU
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 SASU")
    st.markdown("### 👔 Rémunération")
    st.write(f"Rémunération nette : **{remu_net:.0f} €**")
    st.write(f"Charges sociales estimées : **{cot_sasu:.0f} €** ({taux_sasu*100:.0f} %)")
    st.write(f"💸 Coût total entreprise : **{cout_sasu:.0f} €**")

    st.markdown("### 🏢 Société")
    st.write(f"Charges hors rémunération : **{charges:.0f} €**")
    st.write(f"Bénéfice avant IS : **{resultat_sasu:.0f} €**")
    if resultat_sasu <= 42500:
        st.write(f"IS (15%) = **{is_sasu:.0f} €**")
    else:
        tranche1 = 42500 * 0.15
        tranche2 = (resultat_sasu - 42500) * 0.25
        st.write(f"IS : 15% sur 42 500 € = {tranche1:.0f} €")
        st.write(f"     25% sur {resultat_sasu - 42500:.0f} € = {tranche2:.0f} €")
        st.write(f"➡️ Total IS = **{is_sasu:.0f} €**")

    st.markdown("### 💰 Distribution")
    st.write(f"Dividendes nets (après flat tax) : **{div_net_sasu:.0f} €**")
    st.write(f"🟢 Revenu net total : **{revenu_net_sasu:.0f} €** par {frequence.lower()}")

# === Affichage EURL
with col2:
    st.subheader("📊 EURL")
    st.markdown("### 👔 Rémunération")
    st.write(f"Rémunération nette : **{remu_net:.0f} €**")
    st.write(f"Charges sociales estimées : **{cot_eurl:.0f} €** ({taux_eurl*100:.0f} %)")
    st.write(f"💸 Coût total entreprise : **{cout_eurl:.0f} €**")

    st.markdown("### 🏢 Société")
    st.write(f"Charges hors rémunération : **{charges:.0f} €**")
    if eurl_avec_is:
        st.write(f"Bénéfice avant IS : **{resultat_eurl:.0f} €**")
        if resultat_eurl <= 42500:
            st.write(f"IS (15%) = **{is_eurl:.0f} €**")
        else:
            tranche1 = 42500 * 0.15
            tranche2 = (resultat_eurl - 42500) * 0.25
            st.write(f"IS : 15% sur 42 500 € = {tranche1:.0f} €")
            st.write(f"     25% sur {resultat_eurl - 42500:.0f} € = {tranche2:.0f} €")
            st.write(f"➡️ Total IS = **{is_eurl:.0f} €**")
        st.markdown("### 💰 Distribution")
        st.write(f"Dividendes nets (après flat tax) : **{div_net_eurl:.0f} €**")
    else:
        st.info("Rémunération non déductible fiscalement à l'IR")
        st.write(f"Bénéfice avant IR : **{resultat_eurl:.0f} €** (sans salaire)")

    st.write(f"🟢 Revenu net total : **{revenu_net_eurl:.0f} €** par {frequence.lower()}")

# === Graphique comparatif
st.markdown("---")
fig, ax = plt.subplots()
ax.bar(["SASU", "EURL"], [revenu_net_sasu, revenu_net_eurl], color=["#4caf50", "#2196f3"])
ax.set_ylabel(f"Revenu net {frequence.lower()} (€)")
ax.set_title("Comparatif SASU vs EURL")
st.pyplot(fig)

# === Conclusion
diff = revenu_net_sasu - revenu_net_eurl
if diff > 0:
    st.success(f"✅ SASU plus avantageuse de **{diff:.0f} €** par {frequence.lower()}")
elif diff < 0:
    st.error(f"❌ EURL plus avantageuse de **{-diff:.0f} €** par {frequence.lower()}")
else:
    st.info("⚖️ Égalité parfaite.")