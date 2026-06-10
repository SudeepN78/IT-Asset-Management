import sqlite3

conn = sqlite3.connect("assets.db")
c = conn.cursor()

print("\nTables inside assets.db:\n")
tables = c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
print(tables)

