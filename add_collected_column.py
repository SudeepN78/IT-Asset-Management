import sqlite3

DB_NAME = "assets.db"

def add_action_column():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    try:
        c.execute("ALTER TABLE complaints ADD COLUMN action TEXT")
        conn.commit()
        print("✅ 'action' column added successfully")
    except sqlite3.OperationalError as e:
        print("ℹ️ Column already exists or error:", e)

    conn.close()

if __name__ == "__main__":
    add_action_column()
