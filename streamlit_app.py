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
taux_cot_tns = 0.40  # charges sociales sur dividendes EURL TNS au-delà du seuil

ca = st.number_input("💰 Chiffre d'affaires", value=30000) * facteur
charges = st.number_input("💸 Charges hors rémunération", value=0) * facteur
eurl_avec_is = st.checkbox("🏛️ EURL soumise à l'IS")
auto_dividendes = st.checkbox("📌 SASU : percevoir tous les bénéfices comme dividendes")

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
    else:
        return 42500 * 0.15 + (resultat - 42500) * 0.25

cout_sasu = remu_brute_sasu
resultat_sasu = ca - charges - cout_sasu
is_sasu = calcul_is(resultat_sasu)
benefice_net_sasu = resultat_sasu - is_sasu
div_sasu = max(0, benefice_net_sasu) if auto_dividendes else st.number_input("📈 Dividendes SASU", value=5000 * facteur)
div_net_sasu = div_sasu * (1 - taux_flat_tax)
revenu_net_sasu = remu_net + div_net_sasu

cout_eurl = remu_brute_eurl
if eurl_avec_is:
    resultat_eurl = ca - charges - cout_eurl
    is_eurl = calcul_is(resultat_eurl)
    benefice_net_eurl = resultat_eurl - is_eurl
    div_eurl = max(0, benefice_net_eurl)
    div_eurl = st.number_input("📈 Dividendes EURL", value=div_eurl)

    # seuil au-delà duquel les dividendes sont soumis à cotisations sociales (~10% capital fictif 10 000 € ici)
    seuil_dividendes = 1000 * facteur  # ex. 10% d’un capital fictif de 10 000 €
    part_sociale = max(0, div_eurl - seuil_dividendes)
    part_non_sociale = min(div_eurl, seuil_dividendes)

    div_net_sociale = part_sociale * (1 - taux_cot_tns)
    div_net_flat = part_non_sociale * (1 - taux_flat_tax)
    div_net_eurl = div_net_sociale + div_net_flat
else:
    resultat_eurl = ca - charges
    is_eurl = 0
    benefice_net_eurl = resultat_eurl
    div_net_eurl = 0

div_net_eurl = round(div_net_eurl, 2)
revenu_net_eurl = remu_net + div_net_eurl

# Affichage et graphique (inchangé)
# ... reste du code identique ...


✅ Le simulateur prend désormais en compte l’imposition sociale spécifique des dividendes en EURL à l’IS :

Les dividendes supérieurs à 10 % du capital (ici simulé à 10 000 €) sont soumis à ~40 % de charges sociales

Le reste reste taxé à la flat tax de 30 %

L’utilisateur peut saisir manuellement le montant de dividendes EURL


Souhaites-tu maintenant que j’affiche le détail de cette répartition dans les résultats, ou que je rende ce seuil personnalisable ?

