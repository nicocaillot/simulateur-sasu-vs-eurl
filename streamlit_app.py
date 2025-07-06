import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(page_title="Simulateur SASU vs EURL", page_icon="📊", layout="centered")
st.title("🧮 Simulateur SASU vs EURL")

frequence = st.radio("🗓️ Voir les résultats :", ["Année", "Mois"])
facteur = 1 if frequence == "Année" else 1 / 12
mode_saisie = st.radio("💼 Type de rémunération saisie :", ["Nette", "Coût employeur"])

# === Taux fixes
taux_sasu = 0.82
taux_flat_tax = 0.30

# === Entrées utilisateur
ca = st.number_input("💰 Chiffre d'affaires", value=30000) * facteur
charges = st.number_input("💸 Charges hors rémunération", value=0) * facteur
eurl_avec_is = st.checkbox("🏛️ EURL soumise à l'IS")
eurl_auto_dividendes = False
if eurl_avec_is:
    eurl_auto_dividendes = st.checkbox("📌 EURL : percevoir tous les bénéfices comme dividendes")
auto_dividendes = st.checkbox("📌 SASU : percevoir tous les bénéfices comme dividendes")
capital_eurl = st.number_input("📌 Capital social (pour EURL)", value=1000)

# === Taux EURL dynamique
taux_eurl = 0.66 if eurl_avec_is else 0.45
st.caption(f"ℹ️ Taux de charges sociales EURL appliqué : {int(taux_eurl * 100)} %")

# === Calculs de rémunération
if mode_saisie == "Nette":
    remu_net = st.number_input("👤 Rémunération nette souhaitée", value=0) * facteur
    remu_brute_sasu = remu_net * (1 + taux_sasu)
    remu_brute_eurl = remu_net * (1 + taux_eurl)
else:
    remu_brute = st.number_input("👤 Rémunération brute (coût entreprise)", value=0) * facteur
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
    else:
        return 42500 * 0.15 + (resultat - 42500) * 0.25

def calcul_dividendes_net_eurl(dividendes, capital):
    seuil = capital * 0.1
    part_flat_tax = min(dividendes, seuil)
    part_sociale = max(0, dividendes - seuil)
    flat_tax = part_flat_tax * 0.30
    cotisations = part_sociale * 0.45
    net = dividendes - flat_tax - cotisations
    return net, flat_tax, cotisations

# === Calcul SASU
cout_sasu = remu_brute_sasu
resultat_sasu = ca - charges - cout_sasu
is_sasu = calcul_is(resultat_sasu)
benefice_net_sasu = resultat_sasu - is_sasu
div_sasu = max(0, benefice_net_sasu) if auto_dividendes else st.number_input("📈 Dividendes SASU", value=5000 * facteur)
div_net_sasu = div_sasu * (1 - taux_flat_tax)
revenu_net_sasu = remu_net + div_net_sasu

# === Calcul EURL
cout_eurl = remu_brute_eurl
if eurl_avec_is:
    resultat_eurl = ca - charges - cout_eurl
    is_eurl = calcul_is(resultat_eurl)
    benefice_net_eurl = resultat_eurl - is_eurl
    dividendes_eurl = max(0, benefice_net_eurl) if eurl_auto_dividendes else st.number_input("📈 Dividendes EURL", value=5000 * facteur)
    div_net_eurl, flat_tax_eurl, cot_div_eurl = calcul_dividendes_net_eurl(dividendes_eurl, capital_eurl)
    revenu_net_eurl = remu_net + div_net_eurl
else:
    resultat_eurl = ca - charges
    is_eurl = 0
    cot_total = resultat_eurl * taux_eurl
    revenu_net_eurl = resultat_eurl - cot_total
    cot_div_eurl = cot_total

# === Affichage
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 SASU")
    st.write(f"Rémunération nette : **{remu_net:.0f} €**")
    st.write(f"Charges sociales : **{cot_sasu:.0f} €** ({taux_sasu*100:.0f} %)")
    st.write(f"Coût total entreprise : **{cout_sasu:.0f} €**")
    st.write(f"Bénéfice avant IS : **{resultat_sasu:.0f} €**")
    st.write(f"➡️ IS total : **{is_sasu:.0f} €**")
    st.write(f"Dividendes nets : **{div_net_sasu:.0f} €**")
    st.markdown(f"🟢 <strong>Revenu net total :</strong> <span style='color:green'><strong>{revenu_net_sasu:.0f} €</strong></span>", unsafe_allow_html=True)

with col2:
    st.subheader("📊 EURL")
    st.write(f"Rémunération nette : **{remu_net:.0f} €**")
    st.write(f"Charges sociales : **{cot_eurl:.0f} €** ({taux_eurl*100:.0f} %)")
    st.write(f"Coût total entreprise : **{cout_eurl:.0f} €**")
    if eurl_avec_is:
        st.write(f"Bénéfice avant IS : **{resultat_eurl:.0f} €**")
        st.write(f"➡️ IS total : **{is_eurl:.0f} €**")
        st.write(f"Dividendes bruts : **{dividendes_eurl:.0f} €**")
        st.write(f"Flat tax : **{flat_tax_eurl:.0f} €**, Cotisations : **{cot_div_eurl:.0f} €**")
        st.write(f"Dividendes nets : **{div_net_eurl:.0f} €**")
    else:
        st.info("Rémunération non déductible (IR)")
        st.write(f"Charges sociales estimées sur bénéfice : **{cot_div_eurl:.0f} €**")
    st.markdown(f"🟢 <strong>Revenu net total :</strong> <span style='color:green'><strong>{revenu_net_eurl:.0f} €</strong></span>", unsafe_allow_html=True)

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

# === Note
st.markdown("---")
st.markdown("📘 **Note fiscale :**")
st.markdown("- **SASU** : Dividendes soumis à la flat tax de 30 %.")
st.markdown("- **EURL à l’IS** : Flat tax sur 10 % du capital, cotisations sociales (~45 %) au-delà.")
st.markdown("- **EURL à l’IR** : Bénéfice imposé au nom du dirigeant. Pas de distribution de dividendes.")