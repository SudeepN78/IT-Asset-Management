import sqlite3

db = "assets.db"
conn = sqlite3.connect(db)
c = conn.cursor()

print("🔄 Dropping broken assets table...")
c.execute("DROP TABLE IF EXISTS assets")
conn.commit()

print("🔧 Creating new clean assets table...")

c.execute("""
CREATE TABLE assets (
    asset_id TEXT PRIMARY KEY,
    asset_name TEXT,
    model TEXT,
    assigned_to TEXT,
    department TEXT,
    location TEXT,
    purchase_date TEXT,
    warranty_expiry TEXT,
    status TEXT,
    asset_health TEXT,
    usage_hours INTEGER,
    purchase_cost REAL,
    age_days INTEGER,
    warranty_remaining_days INTEGER,
    last_updated TEXT
)
""")

conn.commit()
conn.close()
print("✅ New assets table created successfully!")
