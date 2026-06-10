import sqlite3

DATABASE = "assets.db"

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    conn = get_db()
    c = conn.cursor()

    # USERS
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT,
        email TEXT
    )
    """)

    # ASSETS
    c.execute("""
    CREATE TABLE IF NOT EXISTS assets (
        asset_id TEXT PRIMARY KEY,
        asset_name TEXT,
        location TEXT,
        usage_hours INTEGER DEFAULT 0
    )
    """)

    # ASSET REQUESTS
    c.execute("""
    CREATE TABLE IF NOT EXISTS asset_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee TEXT,
        email TEXT,
        asset_name TEXT,
        requested_location TEXT,
        phone TEXT,
        status TEXT DEFAULT 'Pending',
        hr_message TEXT
    )
    """)

    # COMPLAINTS
    c.execute("""
    CREATE TABLE IF NOT EXISTS complaints (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee TEXT,
        asset_id TEXT,
        complaint TEXT,
        status TEXT DEFAULT 'Pending'
    )
    """)

    conn.commit()
    conn.close()


def get_asset_types():
    conn = get_db()
    c = conn.cursor()

    c.execute("""
        SELECT DISTINCT asset_name
        FROM assets
        WHERE asset_name IS NOT NULL
        ORDER BY asset_name
    """)

    rows = c.fetchall()
    conn.close()

    return [r["asset_name"] for r in rows]