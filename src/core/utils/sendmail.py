import logging
import os

import aiohttp
import requests

logger = logging.getLogger(__name__)

MAILGUN_API_KEY = os.getenv("MAILGUN_API_KEY")
MAILGUN_DOMAIN = os.getenv("MAILGUN_DOMAIN", "waypath.be")
RESET_PASSWORD_URL = os.getenv("RESET_PASSWORD_URL")
FROM_EMAIL = "postmaster@waypath.be"


async def send_reset_email(email: str, token: str) -> None:
    """Send a password reset email using Mailgun."""
    reset_link = f"{RESET_PASSWORD_URL}?token={token}"
    subject = "Password Reset Request"
    text = f"Click the following link to reset your password: {reset_link}"

    if not MAILGUN_API_KEY:
        logger.error("MAILGUN_API_KEY is not set. Cannot send email.")
        raise ValueError("MAILGUN_API_KEY is required to send emails.")  # noqa: TRY003

    try:
        async with (
            aiohttp.ClientSession() as session,
            session.post(
                f"https://api.eu.mailgun.net/v3/{MAILGUN_DOMAIN}/messages",
                auth=aiohttp.BasicAuth("api", MAILGUN_API_KEY),
                data={
                    "from": f"Waypath <{FROM_EMAIL}>",
                    "to": [email],
                    "subject": subject,
                    "text": text,
                },
            ) as response,
        ):
            if response.status != 200:  # noqa: PLR2004
                logger.error("Failed to send email: %s", await response.text())
                response.raise_for_status()
            logger.info("Password reset email sent successfully to %s.", email)
        logger.info("Password reset email sent successfully to %s.", email)
    except requests.RequestException:
        logger.exception("Error sending password reset email to %s.", email)
        raise
