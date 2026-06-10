import joblib
import sqlite3

MODEL_FILE = "trained_asset_life_model.joblib"
EXPECTED_LIFE_DAYS = 1825  # 5 years

model = joblib.load(MODEL_FILE)

def predict_asset_status(asset_id):
    try:
        conn = sqlite3.connect("assets.db")
        conn.row_factory = sqlite3.Row
        c = conn.cursor()

        c.execute("""
            SELECT age_days, usage_hours, warranty_remaining_days
            FROM assets
            WHERE asset_id = ?
        """, (asset_id,))

        asset = c.fetchone()
        conn.close()

        if not asset:
            return {"error": "Asset not found"}

        age_days = max(0, asset["age_days"])
        usage_hours = max(0, asset["usage_hours"])
        warranty_days = asset["warranty_remaining_days"]

        # =====================================
        # 1️⃣ REMAINING LIFE (ML OUTPUT)
        # =====================================
        remaining_days = int(model.predict([[age_days, usage_hours]])[0])
        remaining_days = max(0, remaining_days)

        # =====================================
        # 2️⃣ HEALTH SCORE
        # =====================================
        health = 40 + (remaining_days / EXPECTED_LIFE_DAYS) * 60

        # 🚨 If warranty finished → force health low
        if warranty_days <= 0:
            health = min(health, 30)

        health = int(max(0, min(100, health)))

        # =====================================
        # 3️⃣ CONDITION
        # =====================================
        if health >= 80:
            condition = "Excellent"
        elif health >= 60:
            condition = "Good"
        elif health >= 40:
            condition = "Fair"
        elif health >= 20:
            condition = "Poor"
        else:
            condition = "Critical"

        # =====================================
        # 4️⃣ GRAPH DATA
        # =====================================
        graph_points = [{"x": i, "y": max(0, 100 - i)} for i in range(0, 101, 10)]

        return {
            "remaining_days": remaining_days,
            "health": health,
            "condition": condition,
            "graph_points": graph_points
        }

    except Exception as e:
        print("Prediction error:", e)
        return {"error": "Prediction failed"}