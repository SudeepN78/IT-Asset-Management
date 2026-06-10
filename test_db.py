from db import get_db

conn = get_db()
c = conn.cursor()

c.execute("""
INSERT INTO assets (asset_id, asset_name, location)
VALUES ('A101', 'Laptop', 'Bangalore')
""")

conn.commit()
conn.close()

print("Inserted successfully")