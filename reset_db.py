# reset_db.py
import sqlite3

conn = sqlite3.connect("assets.db")
c = conn.cursor()

# ============================
# CREATE NEW CLEAN TABLES
# ============================

# Users table
c.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    role TEXT
)
""")

# Correct Assets table
c.execute("""
CREATE TABLE IF NOT EXISTS assets (
    asset_id TEXT PRIMARY KEY,
    asset_name TEXT,
    model TEXT,
    department TEXT,
    location TEXT,
    employee_name TEXT,
    purchase_date TEXT,
    warranty_expiry TEXT,
    status TEXT,
    asset_health TEXT,
    usage_hours INTEGER,
    last_updated TEXT
)
""")

# Asset request table
c.execute("""
CREATE TABLE IF NOT EXISTS asset_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee TEXT,
    asset_name TEXT,
    status TEXT
)
""")

conn.commit()
conn.close()

print("✔ NEW DATABASE CREATED SUCCESSFULLY!")