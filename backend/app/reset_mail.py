"""Send password reset links through a STARTTLS SMTP relay."""

from email.message import EmailMessage
import os
import smtplib
import ssl


def send_reset_link(recipient: str, token: str) -> None:
    url = os.environ["PUBLIC_APP_URL"].rstrip("/") + "/reset-password#token=" + token
    message = EmailMessage()
    message["From"] = os.environ["SMTP_FROM"]
    message["To"] = recipient
    message["Subject"] = "Mini LMS — сброс пароля"
    message.set_content(f"Ссылка для сброса действует 30 минут:\n{url}")
    with smtplib.SMTP(os.environ["SMTP_HOST"], int(os.getenv("SMTP_PORT", "587")), timeout=5) as client:
        client.starttls(context=ssl.create_default_context())
        if username := os.getenv("SMTP_USERNAME"):
            client.login(username, os.environ["SMTP_PASSWORD"])
        client.send_message(message, to_addrs=[recipient])
