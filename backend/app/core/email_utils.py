# app/core/email_utils.py

import os
import socket

_original_getaddrinfo = socket.getaddrinfo
def _getaddrinfo_ipv4(host, port, family=0, type=0, proto=0, flags=0):
    return _original_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)
socket.getaddrinfo = _getaddrinfo_ipv4

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM_NAME = os.getenv("SMTP_FROM_NAME", "TextileIntel")


def send_otp_email(to_email: str, otp: str, purpose: str = "login"):
    subject = "Your TextileIntel Verification Code"
    body = f"""
    <div style="font-family:Arial,sans-serif;background:#0b0d12;color:#eaeaea;padding:24px;border-radius:8px">
        <h2 style="color:#4fd1c5">TextileIntel Verification</h2>
        <p>Your one-time verification code is:</p>
        <p style="font-size:28px;font-weight:bold;letter-spacing:4px;color:#f6ad55">{otp}</p>
        <p>This code expires in 5 minutes. If you did not request this, ignore this email.</p>
    </div>
    """

    if not SMTP_USER or not SMTP_PASSWORD:
        # Dev fallback — no SMTP configured, logs to console so you can test locally
        print(f"[DEV OTP EMAIL] To: {to_email} | OTP: {otp}")
        return True

    msg = MIMEMultipart()
    msg["From"] = f"{SMTP_FROM_NAME} <{SMTP_USER}>"
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "html"))

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, to_email, msg.as_string())
        return True
    except Exception as e:
        print(f"[EMAIL ERROR] Failed to send OTP to {to_email}: {e}")
        return False