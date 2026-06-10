import sqlite3

conn = sqlite3.connect("assets.db")
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS return_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_id TEXT NOT NULL,
    employee TEXT NOT NULL,
    issue TEXT NOT NULL,
    status TEXT DEFAULT 'Pending'
)
""")

conn.commit()
conn.close()

print("✅ return_requests table created successfully")
