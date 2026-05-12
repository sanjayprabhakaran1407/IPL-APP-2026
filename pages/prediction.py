import streamlit as st
import pandas as pd

st.title("🤖 Player Performance Prediction")

df = pd.read_csv("ipl_data.zip", compression="zip")
df.columns = df.columns.str.lower()

run_col = "runs_batter" if "runs_batter" in df.columns else "batsman_runs"

player_stats = df.groupby("batter").agg(
    runs=(run_col, "sum"),
    balls=(run_col, "count")
).reset_index()

player_stats["strike_rate"] = (player_stats["runs"] / player_stats["balls"]) * 100
player_stats["consistency"] = player_stats["runs"] / 10

player = st.selectbox("Select Player", sorted(player_stats["batter"]))

data = player_stats[player_stats["batter"] == player].iloc[0]

team = df[df["batter"] == player]["batting_team"].iloc[-1]

# GLASS CARD
st.markdown(f"""
<div style='
background: rgba(255,255,255,0.05);
padding:20px;
border-radius:12px;
'>
<b>{player}</b><br>
Team: {team}
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# METRICS
col1, col2, col3 = st.columns(3)

col1.metric("Runs", int(data["runs"]))
col2.metric("Strike Rate", round(data["strike_rate"], 2))
col3.metric("Consistency", round(data["consistency"], 2))

st.markdown("---")

# PREDICTION BUTTON
if st.button("🚀 Predict Performance"):

    score = (data["runs"] * 0.3) + (data["strike_rate"] * 0.7)

    if score > 180:
        st.success("🔥 High Performance Player")
    elif score > 130:
        st.info("⭐ Consistent Player")
    else:
        st.warning("⚠ Needs Improvement")

st.markdown("---")

# MATCH CARD
st.markdown("""
<div style='
background: rgba(255,255,255,0.05);
padding:20px;
border-radius:12px;
text-align:center;
'>
</div>
""", unsafe_allow_html=True)
