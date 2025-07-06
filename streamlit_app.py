import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(page_title="Simulateur SASU vs EURL", page_icon="📊", layout="centered")
st.title("🧮 Simulateur SASU vs EURL")

frequence = st.radio("🗓️ Voir les résultats :", ["Annuel", "Mensuel"])
facteur = 1 if frequence == "Annuel" else 1 / 12
mode_saisie = st.radio("💼 Type de rémunération saisie :", ["Nette", "Coût employeur"])

taux_sasu = 0.82
taux_eurl = 0.66
taux_flat_tax = 0.30
taux_cot_div_eurl = 0.45

ca = st.number_input("💰 Chiffre d'affaires", value=30000) * facteur
charges = st.number_input("💸 Charges hors rémunération", value=0) * facteur
capital_eurl = st.number_input("🏦 Capital social EURL (€)", value=1000)
dividendes_eurl = st.number_input("📈 Dividendes bruts EURL (€)", value=5000 * facteur)
eurl_avec_is = st.checkbox("🏛️ EURL soumise à l'IS")
auto_dividendes = st.checkbox("📌 SASU : percevoir tous les bénéfices comme dividendes")

# --- Rémunération
if mode_saisie == "Nette":
    remu_net = st.number_input("👤 Rémunération nette souhaitée", value=0) * facteur
    remu_brute_sasu = remu_net * (1 + taux_sasu)
    remu_brute_eurl = remu_net * (1 + taux_eurl)
else:
    remu_brute = st.number_input("👤 Rémunération brute souhaitée", value=0) * facteur
    remu_net = remu_brute / (1 + taux_sasu)
    remu_brute_sasu = remu_brute
    remu_brute_eurl = remu_brute

cot_sasu = remu_brute_sasu - remu_net
cot_eurl = remu_brute_eurl - remu_net

def calcul_is(resultat):
    if resultat <= 0:
        return 0
    if resultat <= 42500:
        return resultat * 0.15
    return 42500 * 0.15 + (resultat - 42500) * 0.25

def calcul_dividendes_net_sasu(dividendes):
    flat_tax = dividendes * taux_flat_tax
    net = dividendes - flat_tax
    return net, flat_tax

def calcul_dividendes_net_eurl(dividendes, capital):
    seuil = 0.10 * capital
    if dividendes <= seuil:
        impots = dividendes * taux_flat_tax
        net = dividendes - impots
        return net, impots, 0
    else:
        flat_part = seuil
        cot_part = dividendes - seuil
        impots = flat_part * taux_flat_tax
        cotisations = cot_part * taux_cot_div_eurl
        net = flat_part - impots + cot_part - cotisations
        return net, impots, cotisations

# === SASU
cout_sasu = remu_brute_sasu
resultat_sasu = ca - charges - cout_sasu
is_sasu = calcul_is(resultat_sasu)
benefice_net_sasu = resultat_sasu - is_sasu
div_sasu = max(0, benefice_net_sasu) if auto_dividendes else st.number_input("📈 Dividendes bruts SASU (€)", value=5000 * facteur)
div_net_sasu, flat_tax_sasu = calcul_dividendes_net_sasu(div_sasu)
revenu_net_sasu = remu_net + div_net_sasu

# === EURL
cout_eurl = remu_brute_eurl
if eurl_avec_is:
    resultat_eurl = ca - charges - cout_eurl
    is_eurl = calcul_is(resultat_eurl)
    benefice_net_eurl = resultat_eurl - is_eurl
    div_net_eurl, flat_tax_eurl, cot_div_eurl = calcul_dividendes_net_eurl(dividendes_eurl, capital_eurl)
    revenu_net_eurl = remu_net + div_net_eurl
else:
    resultat_eurl = ca - charges
    is_eurl = 0
    benefice_net_eurl = resultat_eurl
    div_net_eurl = 0
    flat_tax_eurl = 0
    cot_div_eurl = 0
    revenu_net_eurl = remu_net

# === Affichage
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 SASU")
    st.write(f"Rémunération nette : **{remu_net:.0f} €**")
    st.write(f"Charges sociales : **{cot_sasu:.0f} €** ({taux_sasu*100:.0f}%)")
    st.write(f"Coût total entreprise : **{cout_sasu:.0f} €**")
    st.write(f"Bénéfice avant IS : **{resultat_sasu:.0f} €**")
    st.write(f"IS : **{is_sasu:.0f} €**")
    st.write(f"➡️ Bénéfice après IS : **{benefice_net_sasu:.0f} €**")

    st.markdown("### 💰 Dividendes SASU")
    st.write(f"Dividendes bruts : **{div_sasu:.0f} €**")
    st.write(f"Flat tax (30%) : **{flat_tax_sasu:.0f} €**")
    st.write(f"Dividendes nets : **{div_net_sasu:.0f} €**")
    st.success(f"Revenu net total : **{revenu_net_sasu:.0f} €** par {frequence.lower()}")

with col2:
    st.subheader("📊 EURL")
    st.write(f"Rémunération nette : **{remu_net:.0f} €**")
    st.write(f"Charges sociales : **{cot_eurl:.0f} €** ({taux_eurl*100:.0f}%)")
    st.write(f"Coût total entreprise : **{cout_eurl:.0f} €**")
    st.write(f"Bénéfice avant IS : **{resultat_eurl:.0f} €**")
    st.write(f"IS : **{is_eurl:.0f} €**")
    st.write(f"➡️ Bénéfice après IS : **{benefice_net_eurl:.0f} €**")

    st.markdown("### 💰 Dividendes EURL")
    st.write(f"Dividendes bruts : **{dividendes_eurl:.0f} €**")
    st.write(f"Flat tax (30%) sur 10% du capital : **{flat_tax_eurl:.0f} €**")
    st.write(f"Cotisations sociales (~45%) au-delà : **{cot_div_eurl:.0f} €**")
    st.write(f"Dividendes nets : **{div_net_eurl:.0f} €**")
    st.success(f"Revenu net total : **{revenu_net_eurl:.0f} €** par {frequence.lower()}")

# === Graph
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

# === Note
st.markdown("---")
st.markdown("📘 **Note fiscale :**")
st.markdown("- **Dividendes SASU** : flat tax de 30%")
st.markdown("- **Dividendes EURL à l’IS** :")
st.markdown("  - Flat tax 30% sur 10% du capital social")
st.markdown("  - Cotisations sociales (~45%) au-delà de ce seuil")