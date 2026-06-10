import sqlite3

conn = sqlite3.connect("assets.db")
c = conn.cursor()

c.execute("DROP TABLE IF EXISTS assets")

c.execute("""
CREATE TABLE assets (
    asset_id TEXT PRIMARY KEY,
    asset_name TEXT,
    model TEXT,
    department TEXT,
    location TEXT,
    purchase_date TEXT,
    warranty_expiry TEXT,
    status TEXT,
    asset_health TEXT,
    usage_hours TEXT,
    purchase_cost REAL,
    last_updated TEXT
)
""")

conn.commit()
conn.close()
print("✔ New assets table created successfully.")
