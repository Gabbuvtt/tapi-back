"""
Notification Celery tasks — handles sending emails via SendGrid.
"""

import asyncio
import logging

from infraestructure.queue.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="infraestructure.queue.tasks.notification_tasks.send_campaign_emails")
def send_campaign_emails(campaign_id: str, recipients: list[dict]):
    """
    Send campaign emails to a list of recipients.

    Args:
        campaign_id: The campaign UUID as string.
        recipients: List of dicts with 'email' and 'full_name'.
    """
    asyncio.run(_send_campaign_emails_async(campaign_id, recipients))


async def _send_campaign_emails_async(campaign_id: str, recipients: list[dict]):
    """Async implementation of campaign email sending."""
    from infraestructure.external.sendgrid_client import SendGridClient

    try:
        client = SendGridClient()

        for recipient in recipients:
            try:
                await client.send_email(
                    to_email=recipient["email"],
                    to_name=recipient.get("full_name", ""),
                    subject=recipient.get("subject", "Tienes una promoción especial"),
                    html_content=recipient.get("html_content", ""),
                )
                logger.info(
                    f"Campaign {campaign_id}: Email sent to {recipient['email']}"
                )
            except Exception as e:
                logger.error(
                    f"Campaign {campaign_id}: Failed to send to "
                    f"{recipient['email']}: {e}"
                )

        logger.info(
            f"Campaign {campaign_id}: Sent {len(recipients)} emails"
        )

    except Exception as e:
        logger.error(f"Campaign {campaign_id}: Error: {e}")
        raise


@celery_app.task(name="infraestructure.queue.tasks.notification_tasks.send_single_email")
def send_single_email(to_email: str, to_name: str, subject: str, html_content: str):
    """Send a single email asynchronously."""
    asyncio.run(_send_single_email_async(to_email, to_name, subject, html_content))


async def _send_single_email_async(
    to_email: str, to_name: str, subject: str, html_content: str
):
    from infraestructure.external.sendgrid_client import SendGridClient

    try:
        client = SendGridClient()
        await client.send_email(to_email, to_name, subject, html_content)
        logger.info(f"Email sent to {to_email}")
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        raise
