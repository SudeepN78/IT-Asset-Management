# ml_util.py
import sqlite3
import pandas as pd
import numpy as np
import joblib
import os

DB_PATH = "assets.db"
MODEL_PATH = "trained_asset_life_model.joblib"


# ---------------------- DB UTILITIES ----------------------
def _get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_asset_row(asset_id: str):
    conn = _get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM assets WHERE asset_id = ?", (asset_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    return dict(row)


def _load_model():
    if not os.path.exists(MODEL_PATH):
        return None
    try:
        return joblib.load(MODEL_PATH)
    except:
        return None


# ---------------------- HEALTH CALCULATIONS ----------------------
def _health_from_condition(condition: str) -> int:
    if not condition:
        return 50
    condition = condition.lower().strip()
    mapping = {
        "excellent": 95,
        "good": 80,
        "average": 60,
        "poor": 35,
        "under repair": 20,
        "damaged": 10,
        "disposed": 0,
    }
    return mapping.get(condition, 50)


def _calculate_health(age_days, usage_hours, warranty_days, condition):
    base = _health_from_condition(condition)

    age_penalty = min(age_days / 365 * 10, 30)
    usage_penalty = min((usage_hours / max(age_days * 8, 1)) * 20, 30)

    warranty_bonus = max(min(warranty_days / 365 * 5, 15), 0)

    health = base - age_penalty - usage_penalty + warranty_bonus
    return int(max(0, min(100, round(health))))


# ---------------------- MAIN PREDICTION FUNCTION ----------------------
def predict_asset_status(asset_id: str) -> dict:
    asset = get_asset_row(asset_id)
    if not asset:
        return {"error": f"Asset {asset_id} not found."}

    age_days = int(asset.get("age_days", 0) or 0)
    usage_hours = int(asset.get("usage_hours", 0) or 0)
    warranty_days = int(asset.get("warranty_remaining_days", 0) or 0)
    condition = asset.get("condition", "Unknown")

    # Calculate health
    health = _calculate_health(age_days, usage_hours, warranty_days, condition)

    # Load ML model
    model = _load_model()

    if model:
        X = pd.DataFrame([{
            "age_days": age_days,
            "usage_hours": usage_hours,
            "warranty_remaining_days": warranty_days
        }])
        try:
            remaining_days = int(model.predict(X)[0])
        except:
            remaining_days = warranty_days
    else:
        remaining_days = warranty_days

    # Normalize
    remaining_days = max(0, remaining_days)

    # -------------- FALLBACK MESSAGE --------------
    fallback_note = None
    if remaining_days == 0:
        fallback_note = (
            "This asset's warranty has expired. Health is predicted based on usage."
        )

    # ---------------- USAGE VS LIFE GRAPH ----------------
    graph_points = []
    max_usage = max(usage_hours, 1)

    for i in range(0, 11):
        u = (max_usage * i) / 10
        y = max(0, 100 - (i * 10))  # decreasing life
        graph_points.append({"x": round(u, 2), "y": round(y, 2)})

    # ---------------- RETURN RESULT ----------------
    return {
        "remaining_days": remaining_days,
        "health": health,
        "condition": condition,
        "graph_points": graph_points,
        "original_days": remaining_days,
        "note": fallback_note
    }
