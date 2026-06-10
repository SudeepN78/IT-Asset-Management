import sqlite3

conn = sqlite3.connect("assets.db")
c = conn.cursor()

try:
    c.execute("""
        ALTER TABLE asset_history
        ADD COLUMN timestamp TEXT
    """)
    conn.commit()
    print("✅ timestamp column added")
except Exception as e:
    print("ℹ️ Column already exists or error:", e)

conn.close()

