import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson
from bs4 import BeautifulSoup
import requests
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# CONFIGURATION MOBILE EXTRA-ÉPURÉE
st.set_page_config(page_title="PrediFoot v4.0", layout="centered", initial_sidebar_state="collapsed")

# --- ACTUALISATION AUTOMATIQUE TOUTES LES 10 SECONDES ---
st_autorefresh(interval=10000, limit=None, key="futebol_live_refresh")

# --- SCRAPER GOOGLE SCORES EN TEMPS RÉEL ---
@st.cache_data(ttl=5)
def get_google_live_scores():
    live_matches, finished_matches, upcoming_matches = [], [], []
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36",
            "Accept-Language": "fr-FR,fr;q=0.9"
        }
        url = "https://google.com"
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            match_cards = soup.find_all(attrs={"data-kr": True}) or soup.find_all(class_="K80Oid")
            for card in match_cards:
                text = card.get_text(separator=" ").strip()
                if "En direct" in text or "'" in text:
                    live_matches.append(text)
                elif "Terminé" in text or "Fin" in text:
                    finished_matches.append(text)
                else:
                    upcoming_matches.append(text)
    except:
        pass
    return live_matches, finished_matches, upcoming_matches

# Interface Dark Mode Minimaliste, Épurée et Centrée
st.markdown("""
<style>
    /* Centrage global des titres et textes */
    .element-container, .stMarkdown, h1, h2, h3, p { text-align: center !important; }
    
    .value-bet { background-color: #064e3b; border-left: 5px solid #10b981; padding: 10px; border-radius: 5px; margin-top: 5px; font-weight: bold; text-align: center;}
    .no-value { background-color: #7f1d1d; border-left: 5px solid #ef4444; padding: 10px; border-radius: 5px; margin-top: 5px; font-weight: bold; text-align: center;}
    .kelly-box { background-color: #1e3a8a; border-left: 5px solid #60a5fa; padding: 10px; border-radius: 5px; margin-top: 5px; color: white; font-weight: bold; text-align: center;}
    
    /* Bloc Vainqueur Centré */
    .winner-box { background: linear-gradient(135deg, #1e3a8a, #0d9488); padding: 12px; border-radius: 8px; text-align: center; font-size: 16px; font-weight: bold; margin: 15px auto; color: white; width: 100%; }
    
    /* Correctif de la zone de scores (Hauteur fluide pour éliminer le rectangle noir vide) */
    .live-ticker { background-color: #1a202c; border: 1px solid #2d3748; padding: 10px; border-radius: 8px; margin-bottom: 15px; height: auto !important; min-height: auto !important; text-align: center; }
    .live-status-title { font-weight: bold; font-size: 13px; margin-bottom: 5px; color: #edf2f7; text-align: center; }
    .live-match { color: #f56565; font-weight: bold; font-size: 13px; margin: 2px 0; text-align: center;}
    .finished-match { color: #a0aec0; font-size: 12px; margin: 2px 0; text-align: center;}
    .upcoming-match { color: #3182ce; font-size: 12px; margin: 2px 0; text-align: center;}
    
    /* Centrage du bouton Réinitialiser */
    .stButton { display: flex; justify-content: center; }
    .stButton>button { width: auto !important; min-width: 200px; border-radius: 6px; padding: 6px 16px; font-size: 14px; margin: 0 auto; }
</style>
""", unsafe_allow_html=True)

# Base de données Coupe du Monde 2026
STATS_MONDE = {
    "🇩🇪 Allemagne": {"gf": 2.15, "ga": 1.10}, "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Angleterre": {"gf": 2.25, "ga": 0.75},
    "🇦🇹 Autriche": {"gf": 1.55, "ga": 1.05}, "🇧🇪 Belgique": {"gf": 1.80, "ga": 1.15},
    "🇧🇦 Bosnie-Herzégovine": {"gf": 1.35, "ga": 1.20}, "🇭🇷 Croatie": {"gf": 1.50, "ga": 0.95},
    "🏴󠁧󠁢󠁳󠁣󠁴󠁿 Écosse": {"gf": 1.30, "ga": 1.10}, "🇪🇸 Espagne": {"gf": 2.40, "ga": 0.65},
    "🇫🇷 France": {"gf": 2.35, "ga": 0.80}, "🇮🇹 Italie": {"gf": 1.60, "ga": 0.80},
    "🇳🇴 Norvège": {"gf": 1.70, "ga": 1.15}, "🇳🇱 Pays-Bas": {"gf": 1.95, "ga": 1.05},
    "🇵🇱 Pologne": {"gf": 1.35, "ga": 1.25}, "🇵🇹 Portugal": {"gf": 2.30, "ga": 0.90},
    "🇸🇪 Suède": {"gf": 1.65, "ga": 1.10}, "🇨🇭 Suisse": {"gf": 1.45, "ga": 1.15},
    "🇨🇿 Tchéquie": {"gf": 1.40, "ga": 1.20}, "🇹🇷 Turquie": {"gf": 1.65, "ga": 1.30},
    "🇺🇦 Ukraine": {"gf": 1.40, "ga": 1.10}, "🇦🇷 Argentine": {"gf": 2.20, "ga": 0.70},
    "🇧🇷 Brésil": {"gf": 2.10, "ga": 0.85}, "🇨🇴 Colombie": {"gf": 1.70, "ga": 0.90},
    "🇪🇨 Équateur": {"gf": 1.40, "ga": 1.05}, "🇵🇾 Paraguay": {"gf": 1.10, "ga": 0.95},
    "🇺🇾 Uruguay": {"gf": 1.85, "ga": 1.00}, "🇿🇦 Afrique du Sud": {"gf": 1.20, "ga": 1.05},
    "🇩🇿 Algérie": {"gf": 1.60, "ga": 1.00}, "🇨🇻 Cap-Vert": {"gf": 1.25, "ga": 1.10},
    "🇨🇮 Côte d'Ivoire": {"gf": 1.65, "ga": 1.00}, "🇪🇬 Égypte": {"gf": 1.45, "ga": 0.95},
    "🇬🇭 Ghana": {"gf": 1.30, "ga": 1.35}, "🇲🇦 Maroc": {"gf": 1.75, "ga": 0.70},
    "🇨🇩 RD Congo": {"gf": 1.35, "ga": 1.05}, "🇸🇳 Sénégal": {"gf": 1.65, "ga": 0.85},
    "🇹🇳 Tunisie": {"gf": 1.15, "ga": 0.90}, "🇨🇦 Canada": {"gf": 1.45, "ga": 1.30},
    "🇨🇼 Curaçao": {"gf": 1.15, "ga": 1.45}, "🇺🇸 États-Unis": {"gf": 1.55, "ga": 1.20},
    "🇭🇹 Haïti": {"gf": 1.20, "ga": 1.40}, "🇲🇽 Mexique": {"gf": 1.40, "ga": 1.25},
    "🇵🇦 Panama": {"gf": 1.25, "ga": 1.35}, "🇸🇦 Arabie Saoudite": {"gf": 1.10, "ga": 1.40},
    "🇦🇺 Australie": {"gf": 1.35, "ga": 1.15}, "🇰🇷 Corée du Sud": {"gf": 1.60, "ga": 1.10},
    "🇮🇷 Iran": {"gf": 1.50, "ga": 1.00}, "🇮🇶 Irak": {"gf": 1.30, "ga": 1.20},
    "🇯🇵 Japon": {"gf": 2.05, "ga": 0.95}, "🇯🇴 Jordanie": {"gf": 1.20, "ga": 1.25},
    "🇳🇿 Nouvelle-Zélande": {"gf": 1.10, "ga": 1.30}, "🇺🇿 Ouzbékistan": {"gf": 1.25, "ga": 1.05},
    "🇶🇦 Qatar": {"gf": 1.40, "ga": 1.30}
}

def calculate_poisson_probabilities(home_lambda, away_lambda):
    max_goals = 6
    home_probs = [poisson.pmf(i, home_lambda) for i in range(max_goals)]
    away_probs = [poisson.pmf(i, away_lambda) for i in range(max_goals)]
    m = np.outer(home_probs / sum(home_probs), away_probs / sum(away_probs))
    return np.sum(np.tril(m, -1)), np.sum(np.diag(m)), np.sum(np.triu(m, 1)), m

def apply_kelly_criterion(prob, odds, bankroll, fraction=0.25):
    if odds <= 1: return 0
    f = (prob * (odds - 1) - (1 - prob)) / (odds - 1)
    return max(0, f * fraction * bankroll) if f > 0 else 0

# --- TITRE PRINCIPAL ---
st.markdown("<h1 style='text-align: center;'>⚽ PrediFoot Mobile v4.0</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #a0aec0; font-size: 13px; margin-top: -10px;'>⚡ PRONO PAR ISMAHIL — RÉSULTATS GOOGLE EN DIRECT ⚡</p>", unsafe_allow_html=True)

# --- BANDEAU TEMPS RÉEL (CORRIGÉ SANS BARRE NOIRE VIDE) ---
lives, finished, upcoming = get_google_live_scores()
if lives or finished or upcoming:
    st.markdown('<div class="live-ticker">', unsafe_allow_html=True)
    if lives:
        st.markdown('<div class="live-status-title">🔴 EN DIRECT (GOOGLE)</div>', unsafe_allow_html=True)
        for m in lives: st.markdown(f'<p class="live-match">⚽ {m}</p>', unsafe_allow_html=True)
    elif finished or upcoming:
        st.markdown('<div class="live-status-title">🏁 RÉSULTATS & PROGRAMME DU JOUR</div>', unsafe_allow_html=True)
        for m in finished: st.markdown(f'<p class="finished-match">🏁 {m}</p>', unsafe_allow_html=True)
        for m in upcoming: st.markdown(f'<p class="upcoming-match">⏳ {m}</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
else:
    st.markdown("<p style='color: #a0aec0; font-size: 13px; margin-bottom: 15px; text-align: center;'>Les matchs sont terminés ou aucune rencontre active.</p>", unsafe_allow_html=True)

# GESTION DES CLÉS DE SÉLECTION
if "home_choice" not in st.session_state: st.session_state.home_choice = "-- Choisir une équipe --"
if "away_choice" not in st.session_state: st.session_state.away_choice = "-- Choisir une équipe --"

liste_pays = sorted(list(STATS_MONDE.keys()))
options = ["-- Choisir une équipe --"] + liste_pays

with st.expander("⚙️ Capital & Gestion des Mises", expanded=False):
    bankroll = st.number_input("Capital (€)", min_value=10.0, value=1000.0, step=50.0)
    kelly_fraction = st.slider("Modèle Kelly", min_value=0.05, max_value=1.0, value=0.25, step=0.05)

# --- SÉLECTION DES ÉQUIPES ---
col1, col2 = st.columns(2)
with col1:
    home_team = st.selectbox("Équipe Domicile", options, key="home_select", index=options.index(st.session_state.home_choice))
with col2:
    adv = [p for p in options if p != home_team] if home_team != "-- Choisir une équipe --" else options
    idx_away = adv.index(st.session_state.away_choice) if st.session_state.away_choice in adv else 0
    away_team = st.selectbox("Équipe Extérieur", adv, key="away_select", index=idx_away)

# --- BOUTON DE REINITIALISATION ---
if st.button("🔄 Réinitialiser la sélection"):
    st.session_state.home_choice = "-- Choisir une équipe --"
    st.session_state.away_choice = "-- Choisir une équipe --"
    st.rerun()

st.session_state.home_choice = home_team
st.session_state.away_choice = away_team

# --- BLOC D'ANALYSE ---
if home_team != "-- Choisir une équipe --" and away_team != "-- Choisir une équipe --":
    hl = STATS_MONDE[home_team]["gf"] * STATS_MONDE[away_team]["ga"] / 2.50
    al = STATS_MONDE[away_team]["gf"] * STATS_MONDE[home_team]["ga"] / 2.50
    p_home, p_draw, p_away, matrix = calculate_poisson_probabilities(hl, al)
    over_2_5 = sum(matrix[i, j] for i in range(6) for j in range(6) if (i + j) > 2.5)
    # --- BLOC ENTIÈREMENT CORRIGÉ AVEC INDENTATION STRICTE ---
    if p_home > p_away and p_home > p_draw:
        winner_text = f"🏆 Vainqueur évalué : {home_team} ({p_home:.1%})"
    elif p_away > p_home and p_away > p_draw:
        winner_text = f"🏆 Vainqueur évalué : {away_team} ({p_away:.1%})"
    else:
        if p_home >= p_away:
            winner_text = f"🤝 Pronostic : Victoire ou Nul de {home_team} ({(p_home + p_draw):.1%})"
        else:
            winner_text = f"🤝 Pronostic : Victoire ou Nul de {away_team} ({(p_away + p_draw):.1%})"

    # Affichage du vainqueur centré
    st.markdown(f'<div style="background: linear-gradient(135deg, #1e3a8a, #0d9488); padding: 12px; border-radius: 8px; text-align: center; font-size: 16px; font-weight: bold; margin: 15px auto; color: white;">{winner_text}</div>', unsafe_allow_html=True)

    # Onglets
    tab1, tab3, tab4 = st.tabs(["📊 1N2", "🎯 Scores", "🎲 Pari de valeur"])

    with tab1:
        st.markdown(f"<p style='text-align: center; margin: 5px 0;'>🏠 {home_team} : **{p_home:.1%}** | 🤝 Nul : **{p_draw:.1%}** | 🚀 {away_team} : **{p_away:.1%}**</p>", unsafe_allow_html=True)

    with tab3:
        scores = []
        for i in range(4):
            for j in range(4): 
                scores.append({"s": f"{i} - {j}", "p": matrix[i, j]})
        for row in pd.DataFrame(scores).sort_values(by="p", ascending=False).head(3).itertuples():
            st.markdown(f"<p style='text-align: center; margin: 3px 0;'>🎯 **{row.s}** : **{row.p:.1%}**</p>", unsafe_allow_html=True)

    with tab4:
        market = st.selectbox("Marché :", ["Victoire 1", "Nul N", "Victoire 2", "Plus de 2.5"])
        mapping = {"Victoire 1": p_home, "Nul N": p_draw, "Victoire 2": p_away, "Plus de 2.5": over_2_5}
        prob = mapping[market]
        fair_odds = 1 / max(0.01, prob)
        odds = st.number_input("Cote Bookmaker", min_value=1.01, value=float(round(fair_odds + 0.15, 2)), step=0.05)
        val = odds * prob
        
        if val > 1.04:
            st.markdown(f'<div style="background-color: #064e3b; padding: 10px; border-radius: 5px; margin-top: 5px; font-weight: bold; text-align: center; color: white;">✅ VALUE ! (Indice: {val:.2f})</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="background-color: #1e3a8a; padding: 10px; border-radius: 5px; margin-top: 5px; color: white; font-weight: bold; text-align: center;">Mise Kelly : {apply_kelly_criterion(prob, odds, bankroll, kelly_fraction):.2f}€</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div style="background-color: #7f1d1d; padding: 10px; border-radius: 5px; margin-top: 5px; font-weight: bold; text-align: center; color: white;">❌ PAS DE VALUE (Indice: {val:.2f})</div>', unsafe_allow_html=True)
else:
    st.markdown("<p style='text-align: center; color: #a0aec0; margin-top: 20px;'>💡 Choisissez deux équipes pour lancer l'analyse prédictive.</p>", unsafe_allow_html=True)

   
