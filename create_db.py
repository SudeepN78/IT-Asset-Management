# create_db.py
import sqlite3

conn = sqlite3.connect("assets.db")
c = conn.cursor()
# SQL to create a simplified Employee table

# USERS TABLE
c.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    Employee ID TEXT,
    username TEXT UNIQUE,
    password TEXT,
    role TEXT
)
""")

# ASSETS TABLE — FINAL CORRECT SCHEMA MATCHING CSV + LOADER
c.execute("""
CREATE TABLE IF NOT EXISTS assets (
    asset_id TEXT PRIMARY KEY,
    asset_name TEXT,
    model TEXT,
    serial_number TEXT,
    assigned_to TEXT,
    department TEXT,
    location TEXT,
    purchase_date TEXT,
    warranty_expiry TEXT,
    status TEXT,
    condition TEXT,
    age_days INTEGER,
    warranty_remaining_days INTEGER,
    usage_hours INTEGER DEFAULT 0,
    last_updated TEXT
)
""")

# REQUEST TABLE
c.execute("""
CREATE TABLE IF NOT EXISTS asset_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    asset_id TEXT,
    status TEXT DEFAULT 'Pending'
)
""")

conn.commit()
conn.close()

print("✅ Database created successfully!")
