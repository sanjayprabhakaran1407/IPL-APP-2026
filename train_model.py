import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score
import joblib

# =========================
# LOAD DATA
# =========================
df = pd.read_csv("ipl_data.zip", compression="zip")
df.columns = df.columns.str.lower()

runs_col = "runs_batter" if "runs_batter" in df.columns else "batsman_runs"

# =========================
# PLAYER FEATURES
# =========================
player_stats = df.groupby("batter").agg(
    runs=(runs_col, "sum"),
    balls=(runs_col, "count"),
    fours=(runs_col, lambda x: (x == 4).sum()),
    sixes=(runs_col, lambda x: (x == 6).sum())
).reset_index()

# =========================
# REAL FEATURES
# =========================
player_stats["strike_rate"] = (
    player_stats["runs"] / player_stats["balls"]
) * 100

player_stats["average"] = (
    player_stats["runs"] / 10
)

player_stats["boundary_percent"] = (
    (player_stats["fours"] + player_stats["sixes"])
    / player_stats["balls"]
) * 100

player_stats["consistency"] = (
    player_stats["runs"] / player_stats["balls"]
)

# RECENT FORM
recent = (
    df.groupby("batter")[runs_col]
    .rolling(30, min_periods=1)
    .mean()
    .reset_index()
)

recent_form = recent.groupby("batter")[runs_col].mean().reset_index()
recent_form.columns = ["batter", "recent_form"]

player_stats = player_stats.merge(
    recent_form,
    left_on="batter",
    right_on="batter",
    how="left"
)

# =========================
# TARGET VARIABLE
# =========================
player_stats["selected"] = (
    (
        player_stats["strike_rate"] > 130
    ) &
    (
        player_stats["consistency"] > 1.2
    )
).astype(int)

# =========================
# FEATURES
# =========================
X = player_stats[
    [
        "strike_rate",
        "average",
        "boundary_percent",
        "consistency",
        "recent_form"
    ]
]

y = player_stats["selected"]

# =========================
# TRAIN TEST SPLIT
# =========================
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

# =========================
# SCALING
# =========================
scaler = StandardScaler()

X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# =========================
# MODEL
# =========================
model = LogisticRegression(max_iter=1000)

model.fit(X_train, y_train)

# =========================
# ACCURACY
# =========================
pred = model.predict(X_test)

accuracy = accuracy_score(y_test, pred)

print(f"✅ Model Accuracy: {round(accuracy*100,2)}%")

# =========================
# SAVE MODEL
# =========================
joblib.dump(model, "ipl_model.pkl")
joblib.dump(scaler, "scaler.pkl")

print("✅ ipl_model.pkl saved")
print("✅ scaler.pkl saved")