import sqlite3
import pandas as pd
from sklearn.linear_model import LinearRegression
import joblib

MODEL_PATH = "trained_asset_life_model.joblib"
EXPECTED_LIFE_DAYS = 1825  # 5 years

def train_model():
    print("📌 Loading training data from SQLite...")

    conn = sqlite3.connect("assets.db")

    df = pd.read_sql_query("""
        SELECT age_days, usage_hours
        FROM assets
        WHERE age_days IS NOT NULL AND usage_hours IS NOT NULL
    """, conn)

    conn.close()

    if df.empty:
        print("❌ Not enough data to train model.")
        return

    df["age_days"] = pd.to_numeric(df["age_days"])
    df["usage_hours"] = pd.to_numeric(df["usage_hours"])

    # -------------------------------
    # TARGET = REMAINING LIFE
    # -------------------------------
    df["remaining_life"] = EXPECTED_LIFE_DAYS - df["age_days"]
    df["remaining_life"] = df["remaining_life"].clip(lower=0)

    X = df[["age_days", "usage_hours"]]
    y = df["remaining_life"]

    print("📌 Training Linear Regression model...")
    model = LinearRegression()
    model.fit(X, y)

    joblib.dump(model, MODEL_PATH)
    print("✅ Model trained and saved correctly")

if __name__ == "__main__":
    train_model()
