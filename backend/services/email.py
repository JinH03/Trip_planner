import os
import smtplib
import ssl
from email.message import EmailMessage

from dotenv import load_dotenv

load_dotenv()


SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_FROM = os.getenv("SMTP_FROM")


def send_verification_email(
    to_email: str,
    code: str,
) -> None:
    if not SMTP_HOST:
        raise ValueError("SMTP_HOST is not configured")

    if not SMTP_USER:
        raise ValueError("SMTP_USER is not configured")

    if not SMTP_PASSWORD:
        raise ValueError("SMTP_PASSWORD is not configured")

    if not SMTP_FROM:
        raise ValueError("SMTP_FROM is not configured")

    message = EmailMessage()

    message["Subject"] = "Trip Planner 이메일 인증번호"
    message["From"] = SMTP_FROM
    message["To"] = to_email

    message.set_content(
        f"""
안녕하세요.

Trip Planner 회원가입을 위한 이메일 인증번호입니다.

인증번호: {code}

이 인증번호는 10분 동안 유효합니다.

본인이 요청하지 않았다면 이 이메일을 무시해주세요.

Trip Planner
"""
    )

    with smtplib.SMTP_SSL(
        SMTP_HOST,
        SMTP_PORT,
    ) as smtp:
        smtp.login(
            SMTP_USER,
            SMTP_PASSWORD,
        )

        smtp.send_message(message)