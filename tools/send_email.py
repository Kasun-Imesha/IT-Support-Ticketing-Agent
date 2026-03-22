import os
from dotenv import load_dotenv

_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
load_dotenv(os.path.join(_PROJECT_ROOT, ".env"))

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")


def send_email(to_email: str, subject: str, body: str) -> bool:
    """send an email to a target email

    Args:
        to_email (str): receiver email
        subject (str): subject of the email
        body (str): email body

    Returns:
        bool: if email sending suceeded
    """
    
    try:
        msg = MIMEMultipart()
        msg["From"] = SENDER_EMAIL
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, to_email, msg.as_string())
            
        return True
    except Exception as e:
        print(f"[ERROR] Error sending email: {set(e)}")
        return False
    

def escalate_with_email(issue: str) -> dict:
    """send email escalating unresolved issues

    Args:
        issue (str): issue description

    Returns:
        dict: response dict
    """
    subject = "Escalation: Unresolved IT Issue"
    body = f"""
    Hello IT Support Team,

    The following issue reported by a user could not be resolved by the AI Assistant:

    "{issue}"

    Please investigate and take further action.

    Regards,
    AI Notification Agent
    """
    
    success = send_email(to_email="iamkasunimesha@gmail.com", subject=subject, body=body)
    return {"content": "📧 Email sent to IT support." if success else "⚠️ Failed to send email."}
