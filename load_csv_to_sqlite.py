import sqlite3
import pandas as pd
from datetime import datetime
import os

# -----------------------------------------
# CONFIG
# -----------------------------------------
CSV_FILE = "asset_data_clean.csv"

# FIXED: Absolute path to assets.db
DB_FILE = r"C:\MainProject\it_asset_app_local\assets.db"


# -----------------------------------------
# CREATE TABLE IF NOT EXISTS
# -----------------------------------------
def create_table():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS assets (
            asset_id TEXT PRIMARY KEY,
            asset_name TEXT,
            model TEXT,
            serial_number TEXT,
            assigned_to TEXT,
            department TEXT,
            location TEXT,
            purchase_date TEXT,
            warranty_expiry TEXT,
            status TEXT,
            condition TEXT,
            age_days INTEGER,
            warranty_remaining_days INTEGER,
            usage_hours INTEGER DEFAULT 0,
            last_updated TEXT
        )
    """)

    conn.commit()
    conn.close()


# -----------------------------------------
# LOAD CSV
# -----------------------------------------
def load_csv():
    print(f"\n📌 Loading cleaned CSV: {CSV_FILE}")
    df = pd.read_csv(CSV_FILE)
    print("🔹 Columns:", df.columns.tolist())
    return df


# -----------------------------------------
# INSERT DATA INTO TABLE
# -----------------------------------------
def save_to_db(df):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    print("\n📌 Clearing existing asset data...")
    c.execute("DELETE FROM assets")

    print("📌 Inserting data into assets.db...")

    inserted = 0
    for _, row in df.iterrows():
        c.execute("""
            INSERT INTO assets (
                asset_id, asset_name, model, serial_number, assigned_to,
                department, location, purchase_date, warranty_expiry,
                status, condition, age_days, warranty_remaining_days,
                usage_hours, last_updated
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            row["Asset_ID"],
            row["Asset_Name"],
            row["Model"],
            row["Serial_Number"],
            row["Assigned_To"],
            row["Department"],
            row["Location"],
            row["Purchase_Date"],
            row["Warranty_Expiry"],
            row["Status"],
            row["Condition"],
            int(row["age_days"]),
            int(row["warranty_remaining_days"]),
            0,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))

        inserted += 1

    conn.commit()
    conn.close()

    print(f"✅ Successfully inserted {inserted} records.\n")


# -----------------------------------------
# MAIN
# -----------------------------------------
if __name__ == "__main__":
    create_table()
    df = load_csv()
    save_to_db(df)
    print("🎉 DONE — Database ready!")
