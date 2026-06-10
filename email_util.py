import smtplib
from email.message import EmailMessage

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "sudeepsaxo@gmail.com"       # 🔴 replace
APP_PASSWORD = "ncel fhqg ffip eqsz" # 🔴 replace


def send_email(to, subject, body):
    if not to:
        print("⚠️ Email not provided, skipping email send")
        return

    msg = EmailMessage()
    msg["From"] = SENDER_EMAIL
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        print(f"✅ Email sent to {to}")
    except Exception as e:
        print("❌ Email failed:", e)
