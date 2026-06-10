import sqlite3

DB = "assets.db"

conn = sqlite3.connect(DB)
c = conn.cursor()

# HR user
c.execute("""
INSERT OR IGNORE INTO users (username, password, role)
VALUES (?, ?, ?)
""", ("hr", "123", "HR"))

# Employee user
c.execute("""
INSERT OR IGNORE INTO users (username, password, role)
VALUES (?, ?, ?)
""", ("emp", "123", "EMPLOYEE"))

conn.commit()
conn.close()

print("Users added:\nHR → hr / 123\nEMP → emp / 123")
