import sqlite3
from datetime import datetime

def calculate_usage_hours(purchase_date):
    try:
        d = datetime.strptime(purchase_date, "%Y-%m-%d")
    except:
        d = datetime.strptime(purchase_date, "%d-%m-%Y")

    days = (datetime.now() - d).days
    return max(days * 4, 1)     # assume 4 hrs/day usage

conn = sqlite3.connect("assets.db")
c = conn.cursor()

c.execute("SELECT asset_id, purchase_date FROM assets")
rows = c.fetchall()

for asset_id, purchase_date in rows:
    hrs = calculate_usage_hours(purchase_date)
    c.execute("UPDATE assets SET usage_hours=?, last_updated=? WHERE asset_id=?",
              (hrs, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), asset_id))

conn.commit()
conn.close()

print("Usage hours updated for all assets")
