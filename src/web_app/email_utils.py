from datetime import datetime, timezone
from email.message import EmailMessage

import aiosmtplib
from fastapi.templating import Jinja2Templates

from web_app.config import settings


templates = Jinja2Templates(directory="templates")


async def send_email(
    to_email: str, 
    subject: str, 
    plain_text: str,
    html_content: str | None = None) -> None:
    message = EmailMessage()
    message["From"] = settings.mail_from
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(plain_text)
    
    if html_content:
        message.add_alternative(html_content, subtype="html")
        
    await aiosmtplib.send(
        message,
        hostname=settings.mail_server,
        port=settings.mail_port,
        username=settings.mail_username if settings.mail_username else None,
        password=settings.mail_password if settings.mail_password else None,
        use_tls=settings.mail_use_tls,
    )
    
    
async def send_reset_password_email(to_email: str, token: str) -> None:
    subject = "Reset Your Password"
    reset_link = f"{settings.frontend_url}/reset-password?token={token}"
    
    expires_in_minutes = settings.reset_token_expire_minutes
    
    plain_text = (
        "We received a request to reset the password for your FastAPI Blog account.\n\n"
        f"Reset your password: {reset_link}\n\n"
        f"This link expires in {expires_in_minutes} minutes and can only be used once.\n"
        "If you did not request a password reset, you can safely ignore this email.\n"
    )
    
    html_content = templates.get_template("reset_password_email.html").render(
        reset_link=reset_link,
        expires_in_minutes=expires_in_minutes,
        current_year=datetime.now(timezone.utc).year,
    )
    
    await send_email(to_email, subject, plain_text, html_content)