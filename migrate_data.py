import sqlite3

DB = "assets.db"

conn = sqlite3.connect(DB)
c = conn.cursor()

print("\n▶ Migrating data from assets_old → assets...")

query = """
INSERT INTO assets (
    asset_id,
    asset_name,
    model,
    assigned_to,
    department,
    location,
    purchase_date,
    warranty_expiry,
    status,
    asset_health,
    usage_hours,
    purchase_cost,
    age_days,
    warranty_remaining_days,
    last_updated
)
SELECT
    asset_id,
    asset_name,
    model,
    employee_name,           -- moved to assigned_to
    department,
    location,
    purchase_date,
    warranty_expiry,
    status,
    asset_health,
    usage_hours,
    purchase_cost,
    NULL,                    -- age_days
    NULL,                    -- warranty_remaining_days
    last_updated
FROM assets_old
"""

try:
    c.execute(query)
    conn.commit()
    print("✔ Migration completed successfully!")
except Exception as e:
    print("❌ Error:", e)

conn.close()
