from flask import Flask, render_template, request, redirect, session, jsonify ,flash
import sqlite3
from db import get_db, init_database
# Ensure this function exists in ml_util.py and is callable:
# predict_asset_status(purchase_date_str, warranty_expiry_str, usage_hours)
from ml_util import predict_asset_status 
from config import SECRET_KEY
import smtplib
from email.message import EmailMessage
from email_util import send_email
from datetime import datetime
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash


app = Flask(__name__)
app.secret_key = SECRET_KEY



def get_db():
    conn = sqlite3.connect("assets.db")
    conn.row_factory = sqlite3.Row
    return conn

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


# ---------------------------------------------------
# HOME → redirect to login
# ---------------------------------------------------
@app.route("/")
def home():
    return redirect("/login")


# ---------------------------------------------------
# LOGIN PAGE
# ---------------------------------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        username = request.form["username"].strip().lower()
        password = request.form["password"]
        role = request.form["role"].strip().upper()

        conn = get_db()
        conn.row_factory = sqlite3.Row
        c = conn.cursor()

        c.execute("""
            SELECT * FROM users
            WHERE LOWER(username) = ? AND UPPER(role) = ?
        """, (username, role))

        user = c.fetchone()
        conn.close()

        if user:
            stored_pw = user["password"]

            # ✅ SUPPORT BOTH HASHED + PLAIN PASSWORDS
            if stored_pw == password or check_password_hash(stored_pw, password):
                session["user_id"] = user["id"]
                session["username"] = user["username"]
                session["role"] = user["role"]

                if role == "HR":
                    return redirect("/hr")
                else:
                    return redirect("/employee")

        error = "Invalid username, password, or role"

    return render_template("login.html", error=error)


# ---------------------------------------------------
# HR DASHBOARD
# ---------------------------------------------------

@app.route("/hr")
def hr_dashboard():
    if "role" not in session or session["role"] != "HR":
        return redirect("/login")

    conn = get_db()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # Asset requests
    c.execute("SELECT * FROM asset_requests")
    requests = c.fetchall()

    # Assets
    c.execute("SELECT * FROM assets")
    assets = c.fetchall()

    # ✅ Return requests (THIS WAS NOT REACHING TEMPLATE BEFORE)
    c.execute("""
        SELECT * FROM return_requests
        ORDER BY id DESC
    """)
    return_requests = c.fetchall()

    # Complaints
    c.execute("""
        SELECT id, employee, asset_id, complaint, status
        FROM complaints
        ORDER BY id DESC
    """)
    complaints = c.fetchall()

    conn.close()

    # ✅ SINGLE RETURN — EVERYTHING PASSED TO TEMPLATE
    return render_template(
        "hr_dashboard.html",
        requests=requests,
        assets=assets,
        complaints=complaints,
        return_requests=return_requests
    )


@app.route("/signup", methods=["GET", "POST"])
def signup():
    error = None
    success = None

    if request.method == "POST":
        username = request.form["username"].strip().lower()
        employee_id = request.form["employee_id"].strip()
        password = request.form["password"]
        confirm = request.form["confirm"]

        # 🔐 SECURITY RULE
        if not employee_id.startswith("INFO@"):
            error = "Invalid credentials"

        elif password != confirm:
            error = "Invalid credentials"

        else:
            conn = get_db()
            c = conn.cursor()

            try:
                hashed_pw = generate_password_hash(password)

                c.execute("""
                    INSERT INTO users (username, employee_id, password, role)
                    VALUES (?, ?, ?, 'EMPLOYEE')
                """, (username, employee_id, hashed_pw))

                conn.commit()
                success = "Account created successfully"

            except sqlite3.IntegrityError:
                error = "Invalid credentials"

            finally:
                conn.close()

    return render_template("signup.html", error=error, success=success)
# ---------------------------------------------------
# APPROVE REQUEST
# ---------------------------------------------------
@app.route("/hr/approve/<int:req_id>", methods=["POST"])
def approve_request(req_id):
    if "role" not in session or session["role"] != "HR":
        return redirect("/login")

    location_msg = request.form["location_msg"]
    custom_msg = request.form.get("custom_msg", "")

    conn = get_db()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute("SELECT * FROM asset_requests WHERE id=?", (req_id,))
    req = c.fetchone()

    if not req:
        conn.close()
        return redirect("/hr")

    email = req["email"]
    employee = req["employee"]
    asset = req["asset_name"]

    # ✅ UPDATE STATUS
    c.execute(
        "UPDATE asset_requests SET status='Approved' WHERE id=?",
        (req_id,)
    )
    conn.commit()
    conn.close()

    # 📧 SEND CUSTOM EMAIL
    subject = "Asset Request Approved"
    body = f"""
Hello {employee},

Your request for asset: {asset}
has been APPROVED ✅

📍 Asset available at:
{location_msg}

{custom_msg}

Please collect it from HR.

Regards,
HR Team
"""

    send_email(email, subject, body)

    return redirect("/hr")


@app.route("/hr/reject/<int:req_id>", methods=["POST"])
def reject_request(req_id):
    if "role" not in session or session["role"] != "HR":
        return redirect("/login")

    reason = request.form.get("reject_reason", "Not Stock Available")

    conn = get_db()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # Fetch request
    c.execute("SELECT * FROM asset_requests WHERE id=?", (req_id,))
    req = c.fetchone()

    if not req:
        conn.close()
        return redirect("/hr")

    employee_email = req["email"]
    employee_name = req["employee"]
    asset_name = req["asset_name"]

    # ❌ REJECT REQUEST
    c.execute("""
        UPDATE asset_requests
        SET status='Rejected'
        WHERE id=?
    """, (req_id,))

    conn.commit()
    conn.close()

    # 📧 EMAIL (UNCHANGED)
    try:
        send_email(
            employee_email,
            "Asset Request Rejected",
            f"""
Hello {employee_name},

Your request for asset: {asset_name}
has been REJECTED.

Reason:
{reason}

Please contact HR for more details.

Regards,
HR Team
Ph: 7899394079
"""
        )
    except Exception as e:
        print("Email failed:", e)

    return redirect("/hr")

 
# ---------------------------------------------------
# EMPLOYEE DASHBOARD
# ---------------------------------------------------
@app.route("/employee")
def employee_dashboard():
    if "role" not in session or session["role"] not in ["EMPLOYEE", "HR"]: # HR users might view this too
        return redirect("/login")

    return render_template("employee_dashboard.html")


# ---------------------------------------------------
# EMPLOYEE REQUEST ASSET
# ---------------------------------------------------
@app.route("/request-asset", methods=["GET", "POST"])
def request_asset():
    # 🔐 Login check (ONLY username)
    if "username" not in session:
        return redirect("/login")

    assets = get_asset_types()
    message = error = None

    if request.method == "POST":
        asset_name = request.form.get("asset_name")
        location = request.form.get("location")
        phone = request.form.get("phone")
        email = request.form.get("email")

        if not all([asset_name, location, phone, email]):
            error = "All fields are required"
        else:
            try:
                conn = get_db()
                c = conn.cursor()

                c.execute("""
                    INSERT INTO asset_requests
                    (employee, asset_name, requested_location, phone, email, status)
                    VALUES (?, ?, ?, ?, ?, 'Pending')
                """, (
                    session["username"],
                    asset_name,
                    location,
                    phone,
                    email
                ))

                conn.commit()
                conn.close()

                message = "✅ Asset request submitted successfully!"

            except Exception as e:
                error = f"❌ Error submitting request: {e}"

    return render_template(
        "request_asset.html",
        assets=assets,
        message=message,
        error=error
    )


# ---------------------------------------------------
# HR: VIEW ALL REQUESTS (Optional page)
# ---------------------------------------------------
@app.route("/hr/requests")
def hr_requests():
    if "role" not in session or session["role"] != "HR":
        return redirect("/login")

    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM asset_requests")
    rows = c.fetchall()

    return render_template("hr_requests.html", requests=rows)


# ===================================================
#ASSET PREDICTION ROUTES (NEW ADDITION)
# ===================================================

#ASSET PREDICTION ROUTES (MODIFIED)
# ===================================================
# app.py (Focusing on the /predict-asset route)

@app.route("/predict-asset", methods=["GET", "POST"])
def predict_asset():
    if "role" not in session:
        return redirect("/login")

    conn = get_db()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # Load assets for dropdown
    c.execute("SELECT asset_id, asset_name FROM assets ORDER BY asset_id")
    assets = c.fetchall()

    selected_asset = None
    result = None
    error = None

    if request.method == "POST":

        selected_asset = request.form.get("asset_id")

        if not selected_asset:
            error = "Please select an asset."

        else:
            c.execute("""
                SELECT age_days, usage_hours, warranty_remaining_days
                FROM assets
                WHERE asset_id = ?
            """, (selected_asset,))

            asset = c.fetchone()

            if not asset:
                error = "Asset not found"

            else:

                age_days = int(asset["age_days"] or 0)
                usage_hours = int(asset["usage_hours"] or 0)

                warranty_days = asset["warranty_remaining_days"]

                if warranty_days is None:
                    warranty_days = -1
                else:
                    warranty_days = int(warranty_days)

                EXPECTED_LIFE_DAYS = 1825
                MAX_USAGE_HOURS = 10000

                # -----------------------------
                # REMAINING LIFE
                # -----------------------------
                physical_remaining = max(0, EXPECTED_LIFE_DAYS - age_days)

                # -----------------------------
                # WARRANTY EXPIRED CASE
                # -----------------------------
                if warranty_days <= 0:

                    remaining_days = 0

                    usage_factor = min(1, usage_hours / MAX_USAGE_HOURS)

                    # Force health below 30
                    health = int(30 - (usage_factor * 20))

                    health = max(5, min(30, health))

                    note = "⚠ Warranty expired. Asset health is limited."

                # -----------------------------
                # NORMAL CASE
                # -----------------------------
                else:

                    remaining_days = min(physical_remaining, warranty_days)

                    health = int(40 + (remaining_days / EXPECTED_LIFE_DAYS) * 60)

                    health = max(0, min(100, health))

                    note = None

                # -----------------------------
                # CONDITION
                # -----------------------------
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

                # -----------------------------
                # GRAPH DATA
                # -----------------------------
                usage_percent = min(100, int((usage_hours / MAX_USAGE_HOURS) * 100))

                graph_points = []

                for u in range(0, 101, 10):

                    h = max(20, 100 - u)

                    graph_points.append({
                        "x": u,
                        "y": h
                    })

                graph_points.append({
                    "x": usage_percent,
                    "y": health
                })

                # -----------------------------
                # RESULT
                # -----------------------------
                result = {
                    "remaining_days": remaining_days,
                    "health": health,
                    "condition": condition,
                    "graph_points": graph_points
                }

                if note:
                    result["note"] = note

    conn.close()

    return render_template(
        "predict_asset.html",
        assets=assets,
        selected_asset=selected_asset,
        result=result,
        error=error
    )

    
# ================= EMAIL CONFIG =================
EMAIL_ADDRESS = "sudeepsax@gmail.com"        # HR Gmail
EMAIL_PASSWORD = "ncel fhqg ffip eqsz"    # 16-digit app password

def send_email(subject, body):
    msg = EmailMessage()
    msg["From"] = HR_EMAIL
    msg["To"] = HR_EMAIL   # HR receives request info
    msg["Subject"] = subject
    msg.set_content(body)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(HR_EMAIL, EMAIL_PASS)
        smtp.send_message(msg)
# ===============================================


def send_email(to_email, subject, body):
    try:
        msg = EmailMessage()
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.set_content(body)

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()

        print("📧 Email sent to:", to_email)
    except Exception as e:
        print("❌ Email error:", e)



# API: RETURN ALL ASSETS
# ---------------------------------------------------
@app.route("/api/assets")
def api_assets():
    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT * FROM assets")
    rows = c.fetchall()

    assets = []
    for r in rows:
        # NOTE: Using asset_id from the result set 'r' to ensure correct column names are used.
        assets.append({
            "asset_id": r["asset_id"],
            "asset_name": r["asset_name"],
            "model": r["model"],
            "serial_number": r["serial_number"],
            # Assuming 'assigned_to' or 'employee_name' is used in the DB
            "assigned_to": r.get("assigned_to") or r.get("employee_name", "N/A"), 
            "department": r["department"],
            "location": r["location"],
            "purchase_date": r["purchase_date"],
            "warranty_expiry": r["warranty_expiry"],
            "status": r["status"],
            "usage_hours": r["usage_hours"],
        })

    return jsonify({"status": "success", "data": assets})


# ---------------------------------------------------
# CHATBOT API
# ---------------------------------------------------
@app.route("/chatbot", methods=["POST"])
def chatbot_api():
    user_msg = request.json.get("message", "")
    reply = chatbot(user_msg)
    return jsonify({"reply": reply})
#Sign up 

def send_email(to_email, subject, body):
    import smtplib
    from email.message import EmailMessage

    SENDER_EMAIL = "sudeepsaxo@gmail.com"
    APP_PASSWORD = "ncel fhqg ffip eqsz"

    msg = EmailMessage()
    msg["From"] = SENDER_EMAIL
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER_EMAIL, APP_PASSWORD)
            server.send_message(msg)
            print("✅ Email sent to", to_email)
    except Exception as e:
        print("❌ Email error:", e)

# complaint helper function
def get_assigned_employees_with_assets():
    """
    Returns a dictionary:
    {
        'employee_name': 'ASSET_ID',
        ...
    }
    Based on assets.assigned_to column
    """
    conn = get_db()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute("""
        SELECT assigned_to, asset_id
        FROM assets
        WHERE assigned_to IS NOT NULL
          AND assigned_to != ''
          AND assigned_to != 'Unassigned'
          AND status = 'In Use'
    """)

    rows = c.fetchall()
    conn.close()

    result = {}
    for r in rows:
        result[r["assigned_to"]] = r["asset_id"]

    return result


# ---------------- RAISE COMPLAINT ----------------
@app.route("/raise-complaint", methods=["GET", "POST"])
def raise_complaint():
    if "role" not in session:
        return redirect("/login")

    employees_assets = get_assigned_employees_with_assets()
    message = error = None
    search_results = []

    # -------- SUBMIT COMPLAINT --------
    if request.method == "POST":
        employee = request.form.get("employee")
        asset_id = request.form.get("asset_id")
        issue = request.form.get("issue")
        email = request.form.get("email")

        if not employee or not asset_id or not issue or not email:
            error = "All fields are required"
        else:
            conn = get_db()
            c = conn.cursor()
            c.execute("""
                INSERT INTO complaints (employee, asset_id, complaint, email, status)
                VALUES (?, ?, ?, ?, 'Pending')
            """, (employee, asset_id, issue, email))
            conn.commit()
            conn.close()

            message = "✅ Complaint submitted successfully"

    # -------- TRACK STATUS --------
    search_asset_id = request.args.get("search_asset_id")
    if search_asset_id:
        conn = get_db()
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("""
            SELECT asset_id, complaint, status
            FROM complaints
            WHERE asset_id = ?
            ORDER BY id DESC
        """, (search_asset_id.strip(),))
        search_results = c.fetchall()
        conn.close()

    return render_template(
        "raise_complaint.html",
        employees_assets=employees_assets,
        message=message,
        error=error,
        search_results=search_results
    )


# ---------------- HR UPDATE COMPLAINT STATUS ----------------
@app.route("/update-complaint-status", methods=["POST"])
def update_complaint_status():
    if "role" not in session or session["role"] != "HR":
        return redirect("/login")

    complaint_id = request.form.get("id")
    status = request.form.get("status")
    action = request.form.get("action")

    conn = get_db()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # 1️⃣ Fetch complaint details
    c.execute("""
        SELECT employee, asset_id, email, action
        FROM complaints
        WHERE id = ?
    """, (complaint_id,))
    comp = c.fetchone()

    if not comp:
        conn.close()
        return redirect("/hr")

    employee = comp["employee"]
    asset_id = comp["asset_id"]
    email = comp["email"]
    prev_action = comp["action"]  # Repair / Replace (previous action)

    # 2️⃣ Update complaint record
    c.execute("""
        UPDATE complaints
        SET status = ?, action = ?
        WHERE id = ?
    """, (status, action, complaint_id))

    # 3️⃣ BUSINESS LOGIC
    # ------------------------------------------------

    # 🟡 Pending + Repair
    if status == "Pending" and action == "Repair":
        c.execute("""
            UPDATE assets
            SET status = 'Under Repair',
                assigned_to = ?
            WHERE asset_id = ?
        """, (employee, asset_id))

        mail_body = f"""
Hello {employee},

Your asset is currently UNDER REPAIR.

Asset ID: {asset_id}

Please wait until the repair is completed.

Regards,
HR Asset Department
"""

    # 🔵 Pending + Replace
    elif status == "Pending" and action == "Replace":
        c.execute("""
            UPDATE assets
            SET status = 'Under Repair',
                assigned_to = 'Unassigned'
            WHERE asset_id = ?
        """, (asset_id,))

        mail_body = f"""
Hello {employee},

Your asset replacement process has started.

Asset ID: {asset_id}

Please return the asset to the HR Asset Department.

Regards,
HR Asset Department
"""

    # 🟢 SOLVED (FINAL STATE)
    elif status == "Solved":

        # 🔧 SAME ASSET BACK AFTER REPAIR → IN USE
        if prev_action == "Repair":
            c.execute("""
                UPDATE assets
                SET status = 'In Use',
                    assigned_to = ?
                WHERE asset_id = ?
            """, (employee, asset_id))

            mail_body = f"""
Hello {employee},

Your asset repair has been COMPLETED.

Asset ID: {asset_id}

✔ The same asset has been assigned back to you
✔ You continue to use the same asset.

Regards,
HR Asset Department
"""

        # 🔁 REPLACEMENT COMPLETED → AVAILABLE WITH HR
        elif prev_action == "Replace":
            c.execute("""
                UPDATE assets
                SET status = 'Available',
                    assigned_to = 'Unassigned'
                WHERE asset_id = ?
            """, (asset_id,))

            mail_body = f"""
Hello {employee},

Your asset replacement has been COMPLETED.

Asset ID: {asset_id}

✔ You may request a new asset if required.

Regards,
HR Asset Department
"""

        else:
            mail_body = f"""
Hello {employee},

Your complaint has been resolved.

Asset ID: {asset_id}

Regards,
HR Asset Department
"""

    # ❌ Rejected
    elif status == "Rejected":
        mail_body = f"""
Hello {employee},

Your asset complaint has been REJECTED.

Asset ID: {asset_id}

Please contact HR for clarification.

Regards,
HR Asset Department
"""

    else:
        mail_body = f"""
Hello {employee},

Your complaint status has been updated.

Asset ID: {asset_id}
Status: {status}

Regards,
HR Asset Department
"""

    # 4️⃣ Save changes & send email
    conn.commit()
    conn.close()

    send_email(
        email,
        f"Asset Complaint Update – {asset_id}",
        mail_body
    )

    return redirect("/hr")

# ---------------- COLLECT ASSET ----------------
@app.route("/hr/collect/<int:req_id>", methods=["POST"])
def collect_asset(req_id):
    if "role" not in session or session["role"] != "HR":
        return redirect("/login")

    asset_id = request.form.get("asset_id")
    if not asset_id:
        return redirect("/hr")

    conn = get_db()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # 1️⃣ Get approved request
    c.execute("""
        SELECT employee, asset_name
        FROM asset_requests
        WHERE id = ? AND status = 'Approved' AND collected = 0
    """, (req_id,))
    req = c.fetchone()

    if not req:
        conn.close()
        return redirect("/hr")

    employee = req["employee"]

    # 2️⃣ Assign asset
    c.execute("""
        UPDATE assets
        SET assigned_to = ?, status = 'In Use'
        WHERE asset_id = ?
    """, (employee, asset_id))

    # 3️⃣ Mark request collected
    c.execute("""
        UPDATE asset_requests
        SET collected = 1, status = 'Collected'
        WHERE id = ?
    """, (req_id,))

    # 4️⃣ Save asset history
    c.execute("""
        INSERT INTO asset_history
        (asset_id, employee, action, status, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (
        asset_id,
        employee,
        "Collected",
        "In Use",
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()

    return redirect("/hr")
# ---------------- RETURN ASSET ----------------
@app.route("/return-asset", methods=["GET", "POST"])
def return_asset_page():

    if "username" not in session:
        return redirect("/login")

    error = None
    success = None

    if request.method == "POST":
        asset_id = request.form.get("asset_id")
        issue = request.form.get("issue")

        if not asset_id or not issue:
            error = "All fields are required"

        else:
            conn = get_db()
            conn.row_factory = sqlite3.Row
            c = conn.cursor()

            # 🔎 CHECK ASSET
            c.execute("""
                SELECT assigned_to, status
                FROM assets
                WHERE asset_id = ?
            """, (asset_id,))
            asset = c.fetchone()

            if not asset:
                error = "Asset not found"

            elif asset["assigned_to"] in (None, "", "Unassigned"):
                error = "This asset is already with HR"

            elif asset["status"] != "In Use":
                error = "Asset is not currently in use"

            else:
                # ✅ INSERT RETURN REQUEST (NO ASSET UPDATE HERE)
                c.execute("""
                    INSERT INTO return_requests (asset_id, employee, issue, status)
                    VALUES (?, ?, ?, 'Pending')
                """, (
                    asset_id,
                    asset["assigned_to"],   # 🔥 IMPORTANT FIX
                    issue
                ))

                conn.commit()
                success = "Return request sent to HR successfully"

            conn.close()

    return render_template(
        "return_asset.html",
        error=error,
        success=success
    )


# OPTIONAL SHORT URL (SAFE)
@app.route("/return")
def return_page_redirect():
    return redirect("/return-asset")


@app.route("/hr/collect-return/<int:rid>", methods=["POST"])
def collect_return(rid):

    if "role" not in session or session["role"] != "HR":
        return redirect("/login")

    conn = get_db()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute("""
        SELECT asset_id FROM return_requests
        WHERE id=? AND status='Pending'
    """, (rid,))
    req = c.fetchone()

    if req:
        asset_id = req["asset_id"]

        # ✅ UPDATE DATASET ONLY
        c.execute("""
            UPDATE assets
            SET assigned_to='Unassigned',
                status='Available'
            WHERE asset_id=?
        """, (asset_id,))

        c.execute("""
            UPDATE return_requests
            SET status='Collected'
            WHERE id=?
        """, (rid,))

        conn.commit()

    conn.close()
    return redirect("/hr")


@app.route("/hr/reject-return/<int:rid>", methods=["POST"])
def reject_return(rid):
    if "role" not in session or session["role"] != "HR":
        return redirect("/login")

    conn = get_db()
    c = conn.cursor()

    c.execute("""
        UPDATE return_requests
        SET status='Rejected'
        WHERE id=?
    """, (rid,))

    conn.commit()
    conn.close()
    return redirect("/hr")




@app.route("/get-asset-owner", methods=["POST"])
def get_asset_owner():
    asset_id = request.form.get("asset_id")

    conn = get_db()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute("SELECT assigned_to FROM assets WHERE asset_id = ?", (asset_id,))
    row = c.fetchone()
    conn.close()

    if row and row["assigned_to"]:
        return {"employee": row["assigned_to"]}
    else:
        return {"employee": "Unassigned"}


@app.route("/asset-history")
def asset_history():
    if "role" not in session or session["role"] != "HR":
        return redirect("/login")

    conn = get_db()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute("""
        SELECT asset_id, employee, action, status, timestamp
        FROM asset_history
        ORDER BY timestamp DESC
    """)
    history = c.fetchall()

    conn.close()

    return render_template("asset_history.html", history=history)


# ---------------------------------------------------
# LOGOUT
# ---------------------------------------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# ---------------------------------------------------
# RUN APP
# ---------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
    
