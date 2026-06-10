import sqlite3

conn = sqlite3.connect("assets.db")
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS asset_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_id TEXT,
    employee TEXT,
    action TEXT,
    status TEXT,
    action_date DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()
conn.close()

print("✅ asset_history table created")
