import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(page_title="Simulateur SASU vs EURL", page_icon="📊", layout="centered")
st.title("🧮 Simulateur SASU vs EURL")

# === Période
frequence = st.radio("🗓️ Voir les résultats :", ["Annuel", "Mensuel"])
facteur = 1 if frequence == "Annuel" else 1 / 12

# === Entrées
ca = st.number_input("💰 Chiffre d'affaires", value=80000) * facteur
charges = st.number_input("💸 Charges hors rémunération", value=20000) * facteur
remu_net = st.number_input("👨‍💼 Rémunération NETTE souhaitée", value=13500) * facteur

auto_dividendes = st.checkbox("📌 SASU : percevoir tous les bénéfices comme dividendes")
eurl_avec_is = st.checkbox("🏛️ EURL soumise à l'IS (option fiscale)")

# === Taux réalistes
taux_global_sasu = 0.82  # 82% du net
taux_global_eurl = 0.66  # 66% du net
taux_flat_tax = 0.30

# === Fonction IS
def calcul_is(resultat):
    if resultat <= 0:
        return 0
    if resultat <= 42500:
        return resultat * 0.15
    else:
        return 42500 * 0.15 + (resultat - 42500) * 0.25

# === SASU
cout_total_sasu = remu_net * (1 + taux_global_sasu)
cot_sasu = cout_total_sasu - remu_net
resultat_sasu = ca - charges - cout_total_sasu
is_sasu = calcul_is(resultat_sasu)
dividendes_sasu = max(0, resultat_sasu - is_sasu) if auto_dividendes else st.number_input("📈 Dividendes SASU", value=5000 * facteur)
dividendes_net_sasu = dividendes_sasu * (1 - taux_flat_tax)
total_net_sasu = remu_net + dividendes_net_sasu

# === EURL
cout_total_eurl = remu_net * (1 + taux_global_eurl)
cot_eurl = cout_total_eurl - remu_net
resultat_eurl = ca - charges - cout_total_eurl
if eurl_avec_is:
    is_eurl = calcul_is(resultat_eurl)
    dividendes_net_eurl = max(0, (resultat_eurl - is_eurl)) * (1 - taux_flat_tax)
    total_net_eurl = remu_net + dividendes_net_eurl
else:
    total_net_eurl = remu_net  # IR inclus dans cotisations

# === Affichage
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 SASU")
    st.markdown("### 👔 Rémunération du dirigeant")
    st.write(f"Rémunération nette : **{remu_net:.0f} €**")
    st.write(f"Taux cotisations sociales estimé : **{taux_global_sasu*100:.0f}%**")
    st.write(f"Charges sociales estimées : **{cot_sasu:.0f} €**")
    st.write(f"💸 Coût total entreprise : **{cout_total_sasu:.0f} €**")

    st.markdown("### 🏢 Entreprise")
    st.write(f"Charges hors rémunération : **{charges:.0f} €**")
    st.write(f"Chiffre d'affaires : **{ca:.0f} €**")
    st.write(f"➡️ **Bénéfice entreprise** (avant IS) : **{resultat_sasu:.0f} €**")

    st.markdown("### 🧾 Impôt sur les sociétés (IS)")
    if resultat_sasu <= 42500:
        st.write(f"15% sur {resultat_sasu:.0f} € = **{is_sasu:.0f} €**")
    else:
        tranche1 = 42500 * 0.15
        tranche2 = (resultat_sasu - 42500) * 0.25
        st.write(f"15% sur 42 500 € = {tranche1:.0f} €")
        st.write(f"25% sur {resultat_sasu - 42500:.0f} € = {tranche2:.0f} €")
        st.write(f"➡️ **IS total : {is_sasu:.0f} €**")

    st.markdown("### 💰 Distribution")
    st.write(f"Dividendes nets (flat tax 30%) : **{dividendes_net_sasu:.0f} €**")
    st.write(f"🟢 Revenu net total : **{total_net_sasu:.0f} €** par {frequence.lower()}")

with col2:
    st.subheader("📊 EURL")
    st.markdown("### 👔 Rémunération du dirigeant")
    st.write(f"Rémunération nette : **{remu_net:.0f} €**")
    st.write(f"Taux cotisations sociales estimé : **{taux_global_eurl*100:.0f}%**")
    st.write(f"Charges sociales estimées : **{cot_eurl:.0f} €**")
    st.write(f"💸 Coût total entreprise : **{cout_total_eurl:.0f} €**")

    st.markdown("### 🏢 Entreprise")
    st.write(f"Charges hors rémunération : **{charges:.0f} €**")
    st.write(f"Chiffre d'affaires : **{ca:.0f} €**")
    st.write(f"➡️ **Bénéfice entreprise** (avant IS) : **{resultat_eurl:.0f} €**")

    if eurl_avec_is:
        st.markdown("### 🧾 Impôt sur les sociétés (IS)")
        if resultat_eurl <= 42500:
            st.write(f"15% sur {resultat_eurl:.0f} € = **{is_eurl:.0f} €**")
        else:
            tranche1 = 42500 * 0.15
            tranche2 = (resultat_eurl - 42500) * 0.25
            st.write(f"15% sur 42 500 € = {tranche1:.0f} €")
            st.write(f"25% sur {resultat_eurl - 42500:.0f} € = {tranche2:.0f} €")
            st.write(f"➡️ **IS total : {is_eurl:.0f} €**")

        st.markdown("### 💰 Distribution")
        st.write(f"Dividendes nets (flat tax 30%) : **{dividendes_net_eurl:.0f} €**")

    st.write(f"🟢 Revenu net total : **{total_net_eurl:.0f} €** par {frequence.lower()}")

# === Graphique comparatif
st.markdown("---")
fig, ax = plt.subplots()
ax.bar(["SASU", "EURL"], [total_net_sasu, total_net_eurl], color=["#4caf50", "#2196f3"])
ax.set_ylabel(f"Revenu net {frequence.lower()} (€)")
ax.set_title("Comparatif SASU vs EURL")
st.pyplot(fig)

# === Conclusion
diff = total_net_sasu - total_net_eurl
if diff > 0:
    st.success(f"✅ SASU plus avantageuse de **{diff:.0f} €** par {frequence.lower()}")
elif diff < 0:
    st.error(f"❌ EURL plus avantageuse de **{-diff:.0f} €** par {frequence.lower()}")
else:
    st.info("⚖️ Égalité parfaite.")