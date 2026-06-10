import sqlite3

conn = sqlite3.connect("assets.db")
c = conn.cursor()

print("\n=== USERS TABLE ===")
c.execute("SELECT username, password, role FROM users;")
print(c.fetchall())

conn.close()
