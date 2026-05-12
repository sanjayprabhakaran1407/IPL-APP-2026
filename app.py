import streamlit as st
import pandas as pd

st.set_page_config(page_title="IPL Dashboard", layout="wide")

# =========================
# 🎨 UI STYLE
# =========================
st.markdown("""
<style>
body {
    background-color: #0E1117;
    color: white;
}
.title {
    text-align: center;
    font-size: 50px;
    color: #FFD700;
}
.card {
    background: rgba(255,255,255,0.05);
    padding: 20px;
    border-radius: 15px;
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='title'>🏏 IPL Analytics Dashboard</div>", unsafe_allow_html=True)

# =========================
# LOAD DATA
# =========================
df = pd.read_csv("ipl_data.zip", compression="zip")
df.columns = df.columns.str.lower()

runs_col = "runs_batter" if "runs_batter" in df.columns else "batsman_runs"

# =========================
# 🔍 PLAYER SEARCH (ADVANCED)
# =========================
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.header("🔍 Player Profile")

players = sorted(df["batter"].dropna().unique())
player = st.selectbox("Select Player", players)

player_df = df[df["batter"] == player]

# Basic stats
runs = player_df[runs_col].sum()
balls = len(player_df)
sr = (runs / balls * 100) if balls > 0 else 0
last_match = player_df.iloc[-1][runs_col] if len(player_df) > 0 else 0
consistency = runs / balls if balls > 0 else 0

st.subheader(f"📊 {player} Stats")
st.write(f"Runs: {runs}")
st.write(f"Balls Faced: {balls}")
st.write(f"Strike Rate: {round(sr,2)}")
st.write(f"Last Match Score: {last_match}")
st.write(f"Consistency Score: {round(consistency,3)}")

# Bowling stats (if exists)
if "bowler" in df.columns:
    bowl_df = df[df["bowler"] == player]

    if not bowl_df.empty:
        wickets = bowl_df["is_wicket"].sum() if "is_wicket" in df.columns else 0
        balls_bowled = len(bowl_df)
        runs_conceded = bowl_df[runs_col].sum()
        economy = (runs_conceded / balls_bowled * 6) if balls_bowled > 0 else 0

        st.subheader("🎯 Bowling Stats")
        st.write(f"Wickets: {wickets}")
        st.write(f"Balls Bowled: {balls_bowled}")
        st.write(f"Economy: {round(economy,2)}")

        recent = bowl_df.tail(30)
        st.write(f"Recent Performance (Last 30 balls): {recent[runs_col].sum()} runs")

st.markdown("</div>", unsafe_allow_html=True)

# =========================
# ⚔ PLAYER VS PLAYER
# =========================
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.header("⚔ Player vs Player Matchup")

p1 = st.selectbox("Batter", players, key="p1")
p2 = st.selectbox("Bowler", sorted(df["bowler"].dropna().unique()), key="p2")

matchup = df[(df["batter"] == p1) & (df["bowler"] == p2)]

if not matchup.empty:
    runs_scored = matchup[runs_col].sum()
    balls_faced = len(matchup)
    dismissals = matchup["is_wicket"].sum() if "is_wicket" in df.columns else 0
    sr = (runs_scored / balls_faced * 100) if balls_faced > 0 else 0

    st.subheader(f"{p1} vs {p2}")
    st.write(f"Runs: {runs_scored}")
    st.write(f"Balls: {balls_faced}")
    st.write(f"Dismissals: {dismissals}")
    st.write(f"Strike Rate: {round(sr,2)}")
else:
    st.warning("No matchup data found")

st.markdown("</div>", unsafe_allow_html=True)

# =========================
# 🏟 VENUE ANALYSIS
# =========================


# =========================
# NAVIGATION
# =========================
st.info("👉 Navigate using menu → Analysis / Prediction / IPL 2026")