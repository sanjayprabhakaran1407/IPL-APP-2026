import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# =========================================
# PAGE CONFIG
# =========================================
st.set_page_config(
    page_title="IPL 2026 Intelligence Dashboard",
    layout="wide"
)

# =========================================
# CUSTOM CSS
# =========================================
st.markdown("""
<style>

body {
    background-color: #0b1120;
    color: white;
}

.main {
    background-color: #0b1120;
}

h1,h2,h3,h4 {
    color: white;
}

.stMetric {
    background: rgba(255,255,255,0.05);
    padding: 10px;
    border-radius: 10px;
}

.card {
    background: rgba(255,255,255,0.05);
    padding: 20px;
    border-radius: 15px;
    margin-bottom: 15px;
}

</style>
""", unsafe_allow_html=True)

# =========================================
# TITLE
# =========================================
st.title("🏏 IPL 2026 Intelligence Dashboard")

# =========================================
# LOAD DATA
# =========================================
df = pd.read_csv("ipl_data.zip", compression="zip")

# Lowercase columns
df.columns = df.columns.str.lower()

# =========================================
# COLUMN CHECKING
# =========================================
runs_col = "runs_batter" if "runs_batter" in df.columns else "batsman_runs"

batter_col = "batter" if "batter" in df.columns else "batsman"

team_col = "batting_team"

match_col = "match_id" if "match_id" in df.columns else None

venue_col = "venue" if "venue" in df.columns else None

bowler_col = "bowler" if "bowler" in df.columns else None

wicket_col = "is_wicket" if "is_wicket" in df.columns else None

over_col = "over" if "over" in df.columns else None

# =========================================
# TEAM SHORTCUTS
# =========================================
team_mapping = {
    "CSK": "Chennai",
    "MI": "Mumbai",
    "RCB": "Bangalore",
    "KKR": "Kolkata",
    "SRH": "Hyderabad",
    "RR": "Rajasthan",
    "GT": "Gujarat",
    "LSG": "Lucknow",
    "DC": "Delhi",
    "PBKS": "Punjab"
}

# =========================================
# MATCH SELECTOR
# =========================================
matches = [
    ("CSK", "MI"),
    ("RCB", "KKR"),
    ("SRH", "RR"),
    ("GT", "LSG"),
    ("DC", "PBKS")
]

match_names = [f"{a} vs {b}" for a, b in matches]

selected_match = st.selectbox(
    "Select Match",
    match_names
)

team1 = selected_match.split(" vs ")[0]
team2 = selected_match.split(" vs ")[1]

# =========================================
# FILTER TEAM DATA
# =========================================
team1_key = team_mapping.get(team1, team1)
team2_key = team_mapping.get(team2, team2)

team1_df = df[
    df[team_col]
    .astype(str)
    .str.contains(team1_key, case=False, na=False)
]

team2_df = df[
    df[team_col]
    .astype(str)
    .str.contains(team2_key, case=False, na=False)
]

# =========================================
# TOP CONSISTENT PLAYERS
# =========================================
st.header("🔥 Top Consistent Players")

def get_consistent_players(team_df):

    if team_df.empty:
        return pd.DataFrame()

    stats = team_df.groupby(batter_col).agg(
        runs=(runs_col, "sum"),
        balls=(runs_col, "count")
    ).reset_index()

    stats["consistency"] = (
        stats["runs"] / stats["balls"]
    )

    stats = stats.sort_values(
        "consistency",
        ascending=False
    )

    return stats.head(10)

col1, col2 = st.columns(2)

with col1:
    st.subheader(team1)

    t1 = get_consistent_players(team1_df)

    if not t1.empty:
        st.dataframe(t1, use_container_width=True)
    else:
        st.warning("No data found")

with col2:
    st.subheader(team2)

    t2 = get_consistent_players(team2_df)

    if not t2.empty:
        st.dataframe(t2, use_container_width=True)
    else:
        st.warning("No data found")

        # =========================================
# TOP 50 CONSISTENT PLAYERS RANKING
# =========================================

st.subheader("🏆 Top 50 Consistent IPL Players")

# Player statistics
top_consistency = df.groupby(batter_col).agg(
    runs=(runs_col, "sum"),
    balls=(runs_col, "count")
).reset_index()

# Remove players with very low balls
top_consistency = top_consistency[
    top_consistency["balls"] > 100
]

# Consistency formula
top_consistency["consistency_score"] = (
    top_consistency["runs"] / top_consistency["balls"]
) * 100

# Strike Rate
top_consistency["strike_rate"] = (
    top_consistency["runs"] / top_consistency["balls"]
) * 100

# Ranking
top_consistency = top_consistency.sort_values(
    "consistency_score",
    ascending=False
).reset_index(drop=True)

top_consistency.index += 1

# Top 50
top_50 = top_consistency.head(50)

# Rename columns
top_50.columns = [
    "Player",
    "Runs",
    "Balls",
    "Consistency Score",
    "Strike Rate"
]

# Show dataframe
st.dataframe(
    top_50,
    use_container_width=True,
    height=700
)

# Chart
fig_consistency = px.bar(
    top_50.head(15),
    x="Player",
    y="Consistency Score",
    color="Consistency Score",
    title="Top 15 Most Consistent Players"
)

st.plotly_chart(
    fig_consistency,
    use_container_width=True
)



# =========================================
# POWERPLAY ANALYSIS
# =========================================
st.header("⚡ Powerplay Analysis")

if over_col:

    powerplay_df = df[
        df[over_col] <= 6
    ]

    pp_stats = (
        powerplay_df
        .groupby(team_col)[runs_col]
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )

    fig = px.bar(
        pp_stats,
        title="Top Powerplay Teams"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# =========================================
# FANTASY XI
# =========================================
st.header("🧠 Fantasy XI Suggestions")

fantasy = (
    df.groupby(batter_col)[runs_col]
    .sum()
    .sort_values(ascending=False)
    .head(11)
)

fantasy_df = fantasy.reset_index()

fantasy_df.columns = ["Player", "Runs"]

st.dataframe(
    fantasy_df,
    use_container_width=True
)


# =========================================
# VENUE DIFFICULTY
# =========================================

# =========================
# 🏟 FINAL VENUE ANALYSIS (NO DUPLICATES + REAL DATA)
# =========================
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.header("🏟 Advanced Venue Analysis")

df.columns = df.columns.str.lower()

runs_col = "runs_batter" if "runs_batter" in df.columns else "batsman_runs"

# =========================
# CHECK VENUE COLUMN
# =========================
if "venue" not in df.columns:
    st.error("❌ Venue column missing. Please merge in Stage 3.")
    st.stop()

# =========================
# 🧹 ADVANCED VENUE CLEANING (FIX DUPLICATES)
# =========================
df["venue"] = df["venue"].astype(str).str.lower()

def clean_venue(v):
    if "chidambaram" in v or "chepauk" in v:
        return "MA Chidambaram Stadium"
    elif "wankhede" in v:
        return "Wankhede Stadium"
    elif "chinnaswamy" in v or "bengaluru" in v:
        return "M Chinnaswamy Stadium"
    elif "eden" in v:
        return "Eden Gardens"
    elif "narendra modi" in v or "motera" in v:
        return "Narendra Modi Stadium"
    elif "arun jaitley" in v or "feroz shah kotla" in v:
        return "Arun Jaitley Stadium"
    elif "rajiv gandhi" in v or "hyderabad" in v:
        return "Rajiv Gandhi International Stadium"
    elif "mansingh" in v or "jaipur" in v:
        return "Sawai Mansingh Stadium"
    elif "punjab" in v or "mohali" in v:
        return "PCA Stadium Mohali"
    elif "brabourne" in v:
        return "Brabourne Stadium"
    elif "dy patil" in v:
        return "DY Patil Stadium"
    elif "holkar" in v:
        return "Holkar Stadium"
    elif "kanpur" in v:
        return "Green Park Kanpur"
    elif "guwahati" in v or "barsapara" in v:
        return "Barsapara Stadium"
    elif "ranchi" in v:
        return "JSCA Stadium Ranchi"
    else:
        return v.title()

df["venue"] = df["venue"].apply(clean_venue)

# =========================
# VENUE LIST (NOW CLEAN)
# =========================
available_venues = sorted(df["venue"].unique())

venue = st.selectbox("Select Venue", available_venues)

venue_df = df[df["venue"] == venue]

# =========================
# SAFETY CHECK
# =========================
if venue_df.empty:
    st.warning("No data for this venue")
    st.stop()

# =========================
# MATCH TOTALS
# =========================
match_totals = venue_df.groupby("match_id")[runs_col].sum()

total_matches = venue_df["match_id"].nunique()
avg_score = match_totals.mean()
highest = match_totals.max()
lowest = match_totals.min()

# =========================
# PITCH TYPE
# =========================
if avg_score > 170:
    pitch = "Batting Friendly 🟢"
elif avg_score < 140:
    pitch = "Bowling Friendly 🔴"
else:
    pitch = "Balanced ⚖️"

# =========================
# INNINGS ANALYSIS
# =========================
if "inning" in df.columns:
    first_innings = venue_df[venue_df["inning"] == 1].groupby("match_id")[runs_col].sum().mean()
    second_innings = venue_df[venue_df["inning"] == 2].groupby("match_id")[runs_col].sum().mean()
else:
    first_innings, second_innings = 0, 0

# =========================
# BOUNDARIES
# =========================
fours = venue_df[venue_df[runs_col] == 4].shape[0]
sixes = venue_df[venue_df[runs_col] == 6].shape[0]

# =========================
# TOP PLAYERS
# =========================
top_players = (
    venue_df.groupby("batter")[runs_col]
    .sum()
    .sort_values(ascending=False)
    .head(5)
)

# =========================
# DISPLAY
# =========================
st.subheader(f"📍 {venue}")

c1, c2, c3 = st.columns(3)
c1.metric("Matches", total_matches)
c2.metric("Avg Score", round(avg_score, 2))
c3.metric("Pitch", pitch)

st.write("📈 1st Innings Avg:", round(first_innings, 2))
st.write("📉 2nd Innings Avg:", round(second_innings, 2))

st.write(f"🏆 Highest Score: {int(highest)}")
st.write(f"❄ Lowest Score: {int(lowest)}")

st.write(f"💥 Total Fours: {fours}")
st.write(f"💥 Total Sixes: {sixes}")

st.subheader("🔥 Top Players at this Venue")
st.dataframe(top_players)

# =========================
# ⚔ PACERS vs SPINNERS
# =========================
st.subheader("⚔ Pacers vs Spinners")

if "is_wicket" in df.columns:
    pacers = venue_df[venue_df["over"] <= 10]["is_wicket"].sum()
    spinners = venue_df[venue_df["over"] > 10]["is_wicket"].sum()

    col1, col2 = st.columns(2)
    col1.success(f"🟢 Pacers: {int(pacers)} wickets")
    col2.info(f"🔵 Spinners: {int(spinners)} wickets")

st.markdown("</div>", unsafe_allow_html=True)

# =========================================
# TOP RUN SCORERS
# =========================================
st.header("🏆 Top Run Scorers")

top_runs = (
    df.groupby(batter_col)[runs_col]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

fig3 = px.bar(
    top_runs,
    title="Top IPL Run Scorers"
)

st.plotly_chart(
    fig3,
    use_container_width=True
)

# =========================================
# TEAM RUNS
# =========================================
st.header("📊 Team Total Runs")

team_runs = (
    df.groupby(team_col)[runs_col]
    .sum()
    .sort_values(ascending=False)
)

fig4 = px.pie(
    values=team_runs.values,
    names=team_runs.index,
    title="Team Run Distribution"
)

st.plotly_chart(
    fig4,
    use_container_width=True
)

# =========================================
# FOOTER
# =========================================
st.markdown("---")

st.success("  ")
