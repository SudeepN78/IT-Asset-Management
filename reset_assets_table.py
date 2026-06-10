import sqlite3

DB = "assets.db"
conn = sqlite3.connect(DB)
c = conn.cursor()

print("📌 Dropping old assets table...")
c.execute("DROP TABLE IF EXISTS assets")

print("📌 Creating new assets table (NO asset_health)...")
c.execute("""
CREATE TABLE assets (
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
    usage_hours INTEGER,
    last_updated TEXT
)
""")

conn.commit()
conn.close()
print("✅ assets table created successfully!")
