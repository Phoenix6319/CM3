import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson

# CONFIGURATION MOBILE : "centered" est beaucoup plus lisible sur les smartphones Android
st.set_page_config(page_title="PrediFoot v4.0 Mobile", layout="centered", initial_sidebar_state="collapsed")

# Styles CSS d'interface Premium Dark Mode ajustés pour le tactile Android
st.markdown("""
<style>
    .reportview-container { background: #0e1117; color: #ffffff; }
    .metric-box { background-color: #1e293b; padding: 12px; border-radius: 10px; border-left: 5px solid #3b82f6; margin-bottom: 8px; }
    .value-bet { background-color: #064e3b; border-left: 5px solid #10b981; padding: 12px; border-radius: 5px; margin-top: 5px; font-weight: bold;}
    .no-value { background-color: #7f1d1d; border-left: 5px solid #ef4444; padding: 12px; border-radius: 5px; margin-top: 5px; font-weight: bold;}
    .kelly-box { background-color: #1e3a8a; border-left: 5px solid #60a5fa; padding: 12px; border-radius: 5px; margin-top: 5px; color: white; font-size: 16px;}
    
    /* Optimisation des boutons et onglets pour les pouces sur smartphone */
    .stButton>button { width: 100%; padding: 10px; border-radius: 8px; }
    div[data-baseweb="select"] { font-size: 16px !important; }
</style>
""", unsafe_allow_html=True)

# Base de données officielle Coupe du Monde 2026 (Cameroun OUT, Curaçao IN)
STATS_MONDE = {
    # Europe (UEFA)
    "🇩🇪 Allemagne": {"gf": 2.15, "ga": 1.10}, "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Angleterre": {"gf": 2.25, "ga": 0.75},
    "🇦🇹 Autriche": {"gf": 1.55, "ga": 1.05}, "🇧🇪 Belgique": {"gf": 1.80, "ga": 1.15},
    "🇧🇦 Bosnie-Herzégovine": {"gf": 1.35, "ga": 1.20}, "🇭🇷 Croatie": {"gf": 1.50, "ga": 0.95},
    "🏴󠁧󠁢󠁳󠁣󠁴󠁿 Écosse": {"gf": 1.30, "ga": 1.10}, "🇪🇸 Espagne": {"gf": 2.40, "ga": 0.65},
    "🇫🇷 France": {"gf": 2.35, "ga": 0.80}, "🇮🇹 Italie": {"gf": 1.60, "ga": 0.80},
    "🇳🇴 Norvège": {"gf": 1.70, "ga": 1.15}, "🇳🇱 Pays-Bas": {"gf": 1.95, "ga": 1.05},
    "🇵🇱 Pologne": {"gf": 1.35, "ga": 1.25}, "🇵🇹 Portugal": {"gf": 2.30, "ga": 0.90},
    "🇸🇪 Suède": {"gf": 1.65, "ga": 1.10}, "🇨🇭 Suisse": {"gf": 1.45, "ga": 1.15},
    "🇨🇿 Tchéquie": {"gf": 1.40, "ga": 1.20}, "🇹🇷 Turquie": {"gf": 1.65, "ga": 1.30},
    "🇺🇦 Ukraine": {"gf": 1.40, "ga": 1.10},
    
    # Amérique du Sud (CONMEBOL)
    "🇦🇷 Argentine": {"gf": 2.20, "ga": 0.70}, "🇧🇷 Brésil": {"gf": 2.10, "ga": 0.85},
    "🇨🇴 Colombie": {"gf": 1.70, "ga": 0.90}, "🇪🇨 Équateur": {"gf": 1.40, "ga": 1.05},
    "🇵🇾 Paraguay": {"gf": 1.10, "ga": 0.95}, "🇺🇾 Uruguay": {"gf": 1.85, "ga": 1.00},
    
    # Afrique (CAF)
    "🇿🇦 Afrique du Sud": {"gf": 1.20, "ga": 1.05}, "🇩🇿 Algérie": {"gf": 1.60, "ga": 1.00},
    "🇨🇻 Cap-Vert": {"gf": 1.25, "ga": 1.10}, "🇨🇮 Côte d'Ivoire": {"gf": 1.65, "ga": 1.00},
    "🇪🇬 Égypte": {"gf": 1.45, "ga": 0.95}, "🇬🇭 Ghana": {"gf": 1.30, "ga": 1.35},
    "🇲🇦 Maroc": {"gf": 1.75, "ga": 0.70}, "🇨🇩 RD Congo": {"gf": 1.35, "ga": 1.05},
    "🇸🇳 Sénégal": {"gf": 1.65, "ga": 0.85}, "🇹🇳 Tunisie": {"gf": 1.15, "ga": 0.90},
    
    # Amérique du Nord & Centrale (CONCACAF)
    "🇨🇦 Canada": {"gf": 1.45, "ga": 1.30}, "🇨🇼 Curaçao": {"gf": 1.15, "ga": 1.45},
    "🇺🇸 États-Unis": {"gf": 1.55, "ga": 1.20}, "🇭🇹 Haïti": {"gf": 1.20, "ga": 1.40},
    "🇲🇽 Mexique": {"gf": 1.40, "ga": 1.25}, "🇵🇦 Panama": {"gf": 1.25, "ga": 1.35},
    
    # Asie & Océanie (AFC & OFC)
    "🇸🇦 Arabie Saoudite": {"gf": 1.10, "ga": 1.40}, "🇦🇺 Australie": {"gf": 1.35, "ga": 1.15},
    "🇰🇷 Corée du Sud": {"gf": 1.60, "ga": 1.10}, "🇮🇷 Iran": {"gf": 1.50, "ga": 1.00},
    "🇮🇶 Irak": {"gf": 1.30, "ga": 1.20}, "🇯🇵 Japon": {"gf": 2.05, "ga": 0.95},
    "🇯🇴 Jordanie": {"gf": 1.20, "ga": 1.25}, "🇳🇿 Nouvelle-Zélande": {"gf": 1.10, "ga": 1.30},
    "🇺🇿 Ouzbékistan": {"gf": 1.25, "ga": 1.05}, "🇶🇦 Qatar": {"gf": 1.40, "ga": 1.30}
}

def calculate_poisson_probabilities(home_lambda, away_lambda):
    max_goals = 10
    home_probs = [poisson.pmf(i, home_lambda) for i in range(max_goals)]
    away_probs = [poisson.pmf(i, away_lambda) for i in range(max_goals)]
    home_probs = np.array(home_probs) / sum(home_probs)
    away_probs = np.array(away_probs) / sum(away_probs)
    m = np.outer(home_probs, away_probs)
    return np.sum(np.tril(m, -1)), np.sum(np.diag(m)), np.sum(np.triu(m, 1)), m

def apply_kelly_criterion(prob, odds, bankroll, fraction=0.25):
    if odds <= 1: return 0
    kelly_f = (prob * (odds - 1) - (1 - prob)) / (odds - 1)
    return max(0, kelly_f * fraction * bankroll) if kelly_f > 0 else 0

# --- INTERFACE ADAPTÉE ANDROID ---
st.title("⚽ PrediFoot Mobile v4.0")
st.subheader("Algorithme Poisson & Kelly")

with st.expander("⚙️ Configuration du Capital & Mises", expanded=False):
    bankroll = st.number_input("Capital disponible (€)", min_value=10.0, value=1000.0, step=50.0)
    kelly_fraction = st.slider("Friction du Modèle Kelly", min_value=0.05, max_value=1.0, value=0.25, step=0.05)

liste_pays = sorted(list(STATS_MONDE.keys()))

home_team = st.selectbox("Sélectionnez l'Équipe Domicile (A)", liste_pays, index=liste_pays.index("🇫🇷 France") if "🇫🇷 France" in liste_pays else 0)
liste_adversaires = [p for p in liste_pays if p != home_team]
away_team = st.selectbox("Sélectionnez l'Équipe Extérieur (B)", liste_adversaires, index=liste_adversaires.index("🇧🇷 Brésil") if "🇧🇷 Brésil" in liste_adversaires else 0)

# Diviseur ajusté à 2.50 pour éviter l'inflation artificielle des buts moyens mondiaux
home_lambda = STATS_MONDE[home_team]["gf"] * STATS_MONDE[away_team]["ga"] / 2.50
away_lambda = STATS_MONDE[away_team]["gf"] * STATS_MONDE[home_team]["ga"] / 2.50
p_home, p_draw, p_away, matrix = calculate_poisson_probabilities(home_lambda, away_lambda)

p_home_ht, p_draw_ht, p_away_ht, _ = calculate_poisson_probabilities(home_lambda * 0.38, away_lambda * 0.38)
over_1_5 = sum(matrix[i, j] for i in range(10) for j in range(10) if (i + j) > 1.5)
over_2_5 = sum(matrix[i, j] for i in range(10) for j in range(10) if (i + j) > 2.5)

tab1, tab2, tab3, tab4 = st.tabs(["📊 1N2", "⚽ Buts", "🎯 Scores", "🎲 Value Bet"])

with tab1:
    st.write("**Match Complet (90 min)**")
    st.info(f"Victoire {home_team} : **{p_home:.1%}**")
    st.info(f"Match Nul (N) : **{p_draw:.1%}**")
    st.info(f"Victoire {away_team} : **{p_away:.1%}**")
    st.write("**Première Mi-temps (45 min)**")
    st.warning(f"Gagnant MT Domicile : **{p_home_ht:.1%}**")
    st.warning(f"Nul à la Mi-temps : **{p_draw_ht:.1%}**")
    st.warning(f"Gagnant MT Extérieur : **{p_away_ht:.1%}**")

with tab2:
    st.metric("Plus de 1.5 Buts", f"{over_1_5:.1%}", delta=f"Moins: {1-over_1_5:.1%}", delta_color="inverse")
    st.metric("Plus de 2.5 Buts", f"{over_2_5:.1%}", delta=f"Moins: {1-over_2_5:.1%}", delta_color="inverse")
    p_btts_yes = max(0.0, 1.0 - (poisson.pmf(0, home_lambda) * poisson.pmf(0, away_lambda)))
    st.metric("Les deux marquent (BTTS)", f"{p_btts_yes:.1%}")

with tab3:
    scores_list = []
    for i in range(4):
        for j in range(4):
            scores_list.append({"Score": f"{i} - {j}", "Prob": matrix[i, j]})
    df_scores = pd.DataFrame(scores_list).sort_values(by="Prob", ascending=False).head(5)
    for index, row in df_scores.iterrows():
        st.write(f"🎯 Score exact **{row['Score']}** : **{row['Prob']:.1%}** de chance")

with tab4:
    market_to_bet = st.selectbox("Marché à évaluer :", ["Victoire 90' (1)", "Nul 90' (N)", "Victoire 90' (2)", "Plus de 2.5 Buts"])
    market_mapping = {"Victoire 90' (1)": p_home, "Nul 90' (N)": p_draw, "Victoire 90' (2)": p_away, "Plus de 2.5 Buts": over_2_5}
    
    chosen_prob = market_mapping[market_to_bet]
    fair_odds = 1 / max(0.01, chosen_prob)
    bookmaker_odds = st.number_input(f"Cote Bookmaker :", min_value=1.01, value=float(round(fair_odds + 0.15, 2)), step=0.05)
    
    value_index = bookmaker_odds * chosen_prob
    mise_kelly = apply_kelly_criterion(chosen_prob, bookmaker_odds, bankroll, fraction=kelly_fraction)
    
    st.write(f"Cote Juste Estimée : **{fair_odds:.2f}**")
    if value_index > 1.04: 
        st.markdown("<div class='value-bet'>🔥 VALUE DETECTÉE</div>", unsafe_allow_html=True)
    else: 
        st.markdown("<div class='no-value'>PAS DE VALUE</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='kelly-box'>💰 Misez : <b>{mise_kelly:.2f} €</b></div>", unsafe_allow_html=True)

# --- SIGNATURE VISUELLE EN BLOC ---
st.markdown("""
<div style="background-color: #1e293b; padding: 15px; border-radius: 10px; border: 1px solid #38bdf8; text-align: center; margin-top: 30px;">
    <b style="color: #38bdf8; font-size: 14px; letter-spacing: 2px;">⚡ PRONO PAR ISMAHIL ⚡</b>
    <p style="color: #94a3b8; margin: 3px 0 0 0; font-size: 10px;">PRONOSTICS QUANTANTIQUES COUPE DU MONDE</p>
</div>
""", unsafe_allow_html=True)

