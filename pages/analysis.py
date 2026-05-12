import streamlit as st
import pandas as pd
import plotly.express as px

st.title("📊 IPL Player Analysis")

# Load dataset
df = pd.read_csv("ipl_data.zip", compression="zip")
df.columns = df.columns.str.lower()

run_col = "runs_batter" if "runs_batter" in df.columns else "batsman_runs"

# Player stats
player_stats = df.groupby("batter").agg(
    runs=(run_col, "sum"),
    balls=(run_col, "count")
).reset_index()

player_stats["strike_rate"] = (player_stats["runs"] / player_stats["balls"]) * 100

# 🔥 TEAM FILTER (NEW FEATURE)
st.subheader("🔍 Search by Team")

teams = sorted(df["batting_team"].dropna().unique())
selected_team = st.selectbox("Select Team", teams)

team_players = df[df["batting_team"] == selected_team]

top_players = team_players.groupby("batter")[run_col].sum().sort_values(ascending=False).head(10)

st.markdown(f"### 🏏 Top Players - {selected_team}")

for player, runs in top_players.items():
    st.markdown(f"""
    <div style='
        background: rgba(255,255,255,0.05);
        padding:10px;
        margin:5px;
        border-radius:10px;
        transition:0.3s;
    '>
    <b>{player}</b> — {runs} runs
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# PLAYER SELECT
player = st.selectbox("Select Player", sorted(player_stats["batter"]))

data = player_stats[player_stats["batter"] == player].iloc[0]

team = df[df["batter"] == player]["batting_team"].iloc[-1]

st.markdown(f"""
### 🧾 Player Info
Player: {player}  
Team: {team}
""")

# METRICS
col1, col2 = st.columns(2)

col1.metric("Runs", int(data["runs"]))
col2.metric("Strike Rate", round(data["strike_rate"], 2))

st.markdown("---")

# CHARTS
st.subheader("📈 Top Players")

top = player_stats.sort_values("runs", ascending=False).head(10)
fig = px.bar(top, x="batter", y="runs", color="runs")
st.plotly_chart(fig, use_container_width=True)

st.subheader("⚡ Performance Distribution")

fig2 = px.scatter(player_stats, x="runs", y="strike_rate", color="strike_rate")
st.plotly_chart(fig2, use_container_width=True)
