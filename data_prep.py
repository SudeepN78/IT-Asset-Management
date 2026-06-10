# backend/data_pre.py

import pandas as pd
import os
from datetime import datetime

# -------------------------------
# 1. Correct CSV file name
# -------------------------------
CSV_FILE = "it_asset_dataset.csv"     # <-- MATCHES YOUR FILE

# -------------------------------
# 2. Load CSV safely
# -------------------------------
def clean_and_analyze():

    print(f"\n📌 Loading CSV: {CSV_FILE}")

    if not os.path.exists(CSV_FILE):
        raise FileNotFoundError(f"❌ CSV not found: {CSV_FILE}")

    df = pd.read_csv(CSV_FILE)

    print("✔ CSV Loaded")
    print(f"Rows: {len(df)}")
    print(f"Columns: {df.columns.tolist()}")

    # --------------------------------------
    # 3. Normalize column names
    # --------------------------------------
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    # Expected required columns
    required_cols = [
        "asset_id", "asset_name", "model", "assigned_to",
        "department", "location", "purchase_date",
        "warranty_expiry", "status", "condition"
    ]

    missing = [c for c in required_cols if c not in df.columns]

    if missing:
        raise ValueError(f"❌ Missing columns in CSV: {missing}")

    # --------------------------------------
    # 4. Convert purchase_date + warranty_expiry
    # --------------------------------------
    def fix_date(x):
        try:
            return datetime.strptime(x, "%d-%m-%Y").strftime("%Y-%m-%d")
        except:
            return None

    df["purchase_date"] = df["purchase_date"].apply(fix_date)
    df["warranty_expiry"] = df["warranty_expiry"].apply(fix_date)

    # --------------------------------------
    # 5. Clean assigned_to column
    # --------------------------------------
    df["assigned_to"] = df["assigned_to"].fillna("").replace({" ": "", "": "Unassigned"})

    # --------------------------------------
    # 6. Add usage_hours (generate dynamically)
    # --------------------------------------
    import random
    df["usage_hours"] = df.apply(
        lambda row: random.randint(500, 5000) if row["status"] == "In Use" else 0,
        axis=1
    )

    # --------------------------------------
    # 7. Add last_updated column
    # --------------------------------------
    df["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # --------------------------------------
    # 8. Save cleaned CSV
    # --------------------------------------
    output_file = "asset_data_clean.csv"
    df.to_csv(output_file, index=False)

    print(f"\n✔ Cleaned dataset saved → {output_file}")
    print(f"Preview:\n{df.head(5)}")


# Run script
if __name__ == "__main__":
    clean_and_analyze()
