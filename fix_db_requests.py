# fix_db_requests.py
import sqlite3

conn = sqlite3.connect("assets.db")
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS asset_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee TEXT,
    email TEXT,
    asset_name TEXT,
    requested_location TEXT,
    phone TEXT,
    status TEXT DEFAULT 'Pending'
)
""")

conn.commit()
conn.close()
print("✅ asset_requests table updated")
