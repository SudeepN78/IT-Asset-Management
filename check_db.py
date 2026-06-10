import sqlite3

DB_FILE = 'assets.db'

def check_database():
    conn = None
    try:
        # 1. Connect to the database file
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        
        # 2. Execute a simple query to fetch the count and a sample row
        c.execute("SELECT COUNT(*) FROM assets")
        count = c.fetchone()[0]
        print(f"Total rows found in 'assets' table: {count}")

        c.execute("SELECT * FROM assets LIMIT 1")
        sample_row = c.fetchone()
        print(f"Sample data row: {sample_row}")
        
    except sqlite3.Error as e:
        # This catches errors like 'no such table: assets' or file path issues
        print(f"❌ Database Access Error: {e}")
        
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    check_database()