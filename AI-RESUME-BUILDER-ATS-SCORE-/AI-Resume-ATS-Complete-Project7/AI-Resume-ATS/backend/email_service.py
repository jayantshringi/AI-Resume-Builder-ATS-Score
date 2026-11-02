import os
import re
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

def send_contact_notification(name, sender_email, category, subject, message,
                              general_email, support_email):
    load_dotenv(override=True)
    host = os.getenv("SMTP_HOST", "").strip()
    port_raw = os.getenv("SMTP_PORT", "587").strip()
    try:
        port = int(port_raw) if port_raw else 587
    except ValueError:
        port = 587

    username = os.getenv("SMTP_USERNAME", "").strip()
    password = os.getenv("SMTP_PASSWORD", "").strip().replace(" ", "")
    from_email = os.getenv("MAIL_FROM", username).strip()

    if not all([host, username, password, from_email]):
        return False, "SMTP settings are missing or incomplete."

    # Sanitize category, subject, and name to prevent email header injection
    clean_category = re.sub(r"[\r\n]+", " ", category).strip()
    clean_subject = re.sub(r"[\r\n]+", " ", subject).strip()
    clean_name = re.sub(r"[\r\n]+", " ", name).strip()
    clean_sender = re.sub(r"[\r\n]+", "", sender_email).strip()

    # Routing rule:
    # 1. "Suggestion" and "Technical Issues" -> To: mohitki7780264@gmail.com, Cc: adityasing9508@gmail.com
    # 2. "Complaint" and "General Query" -> To: adityasing9508@gmail.com, Cc: mohitki7780264@gmail.com
    mohit_email = general_email if general_email else "mohitki7780264@gmail.com"
    aditya_email = support_email if support_email else "adityasing9508@gmail.com"

    cat_norm = clean_category.lower()
    if "suggestion" in cat_norm or "technic" in cat_norm:
        primary_to = mohit_email
        primary_cc = aditya_email
    else:
        primary_to = aditya_email
        primary_cc = mohit_email

    msg = EmailMessage()
    msg["Subject"] = f"[Resume ATS {clean_category}] {clean_subject}"
    msg["From"] = from_email
    msg["To"] = primary_to
    if primary_cc and primary_cc != primary_to:
        msg["Cc"] = primary_cc
    msg["Reply-To"] = clean_sender
    msg.set_content(
        f"New website contact message\n\n"
        f"Name: {clean_name}\n"
        f"Email: {clean_sender}\n"
        f"Message Type: {clean_category}\n"
        f"Subject: {clean_subject}\n\n"
        f"Routing Details:\n"
        f"  To: {primary_to}\n"
        f"  Cc: {primary_cc}\n\n"
        f"Message:\n{message}\n"
    )

    try:
        # Port 465 is dedicated SSL/SMTPS; ports 587/25 use STARTTLS
        if port == 465:
            with smtplib.SMTP_SSL(host, port, timeout=10) as server:
                server.ehlo()
                server.login(username, password)
                server.send_message(msg)
        else:
            with smtplib.SMTP(host, port, timeout=10) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(username, password)
                server.send_message(msg)
        return True, "sent"
    except Exception as exc:
        return False, str(exc)
