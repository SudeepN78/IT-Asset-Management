# fix_asset_requests.py
import sqlite3

conn = sqlite3.connect("assets.db")
c = conn.cursor()

c.execute("DROP TABLE IF EXISTS asset_requests")

c.execute("""
CREATE TABLE asset_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee TEXT,
    asset_name TEXT,
    requested_location TEXT,
    phone TEXT,
    status TEXT DEFAULT 'Pending',
    approved_asset_id TEXT,
    approved_location TEXT
)
""")

conn.commit()
conn.close()

print("✅ asset_requests table fixed")
