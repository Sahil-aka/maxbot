import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()


def send_email(to_address: str, subject: str, body: str, from_address: str = None, password: str = None) -> str:
    from_address = from_address or os.getenv("EMAIL_ADDRESS")
    password = password or os.getenv("EMAIL_PASSWORD")

    if not from_address or not password:
        return (
            "Email credentials not configured.\n"
            "Please set EMAIL_ADDRESS and EMAIL_PASSWORD in your .env file.\n"
            "Use a Gmail App Password (not your regular password)."
        )

    try:
        msg = MIMEMultipart()
        msg["From"] = from_address
        msg["To"] = to_address
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=10) as server:
            server.login(from_address, password)
            server.send_message(msg)

        return f"Email sent successfully to **{to_address}**!"

    except smtplib.SMTPAuthenticationError:
        return (
            "Gmail authentication failed.\n"
            "Make sure you're using an **App Password** (not your regular Gmail password).\n"
            "Go to: myaccount.google.com → Security → App passwords"
        )
    except smtplib.SMTPRecipientsRefused:
        return f"Invalid recipient address: {to_address}"
    except Exception as e:
        return f"Error sending email: {str(e)}"
