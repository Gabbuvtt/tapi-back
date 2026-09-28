"""
SendGrid email client.

Provides a simple interface for sending transactional and
marketing emails through SendGrid's API.
"""

import logging

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content

from core.config import settings
from core.exceptions import ExternalServiceError

logger = logging.getLogger(__name__)


class SendGridClient:
    """Client for sending emails via SendGrid."""

    def __init__(self):
        self._client = SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
        self._from_email = settings.SENDGRID_FROM_EMAIL

    async def send_email(
        self,
        to_email: str,
        to_name: str,
        subject: str,
        html_content: str,
    ) -> bool:
        """
        Send a single email.

        Args:
            to_email: Recipient email address.
            to_name: Recipient name.
            subject: Email subject line.
            html_content: HTML body content.

        Returns:
            True if sent successfully.

        Raises:
            ExternalServiceError: If SendGrid API fails.
        """
        message = Mail(
            from_email=Email(self._from_email, "TAPI"),
            to_emails=To(to_email, to_name),
            subject=subject,
            html_content=Content("text/html", html_content),
        )

        try:
            response = self._client.send(message)
            if response.status_code not in (200, 201, 202):
                raise ExternalServiceError(
                    service="SendGrid",
                    detail=f"SendGrid returned status {response.status_code}",
                )
            logger.info(f"Email sent to {to_email} (status: {response.status_code})")
            return True

        except Exception as e:
            logger.error(f"SendGrid error sending to {to_email}: {e}")
            raise ExternalServiceError(
                service="SendGrid",
                detail=str(e),
            )

    def build_promotion_email(
        self,
        business_name: str,
        customer_name: str,
        promotion_title: str,
        promotion_message: str,
        cta_url: str,
    ) -> str:
        """
        Build an HTML email template for a promotion.

        Args:
            business_name: The sending business's name.
            customer_name: The recipient's name.
            promotion_title: Title of the promotion.
            promotion_message: Body message.
            cta_url: Call-to-action button URL.

        Returns:
            HTML string for the email body.
        """
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 0; background-color: #f4f4f5;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background: linear-gradient(135deg, #6366f1, #8b5cf6); border-radius: 16px 16px 0 0; padding: 32px; text-align: center;">
                    <h1 style="color: white; margin: 0; font-size: 28px;">🎉 {promotion_title}</h1>
                    <p style="color: rgba(255,255,255,0.9); margin-top: 8px;">De parte de {business_name}</p>
                </div>
                <div style="background: white; padding: 32px; border-radius: 0 0 16px 16px;">
                    <p style="color: #374151; font-size: 16px;">Hola <strong>{customer_name}</strong>,</p>
                    <p style="color: #6b7280; font-size: 15px; line-height: 1.6;">{promotion_message}</p>
                    <div style="text-align: center; margin: 32px 0;">
                        <a href="{cta_url}" style="background: #6366f1; color: white; padding: 14px 32px; border-radius: 8px; text-decoration: none; font-weight: 600; font-size: 16px;">
                            Ver promoción
                        </a>
                    </div>
                    <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 24px 0;">
                    <p style="color: #9ca3af; font-size: 12px; text-align: center;">
                        Recibiste este email porque eres cliente de {business_name} a través de TAPI.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
