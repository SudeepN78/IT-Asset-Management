import sqlite3

conn = sqlite3.connect("assets.db")
c = conn.cursor()

try:
    c.execute("ALTER TABLE complaints ADD COLUMN email TEXT")
    conn.commit()
    print("✅ Email column added")
except Exception as e:
    print("ℹ", e)

conn.close()
