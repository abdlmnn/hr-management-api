from celery import shared_task
from .models import EmailNotification
from src.utils import email_notification_body
from django.utils import timezone
import os
from django.core.mail import EmailMessage, get_connection


@shared_task(bind=True)
def bulk_send_email_nofication(self):
    notifications = EmailNotification.objects.filter(
        is_sent=False,
        date_created__date=timezone.now().date(),
    )

    if not notifications.exists():
        return "No pending email notifications."

    # Prepare email messages in bulk
    messages = []
    for n in notifications:
        html_content = email_notification_body(email_body=n.body)
        msg = EmailMessage(
            subject=n.subject,
            body=html_content,
            from_email=os.getenv("EMAIL_HOST_USER"),
            to=[n.recipient],
        )
        msg.content_subtype = "html"
        messages.append(msg)

    # Send all emails in one SMTP session
    try:
        with get_connection() as connection:
            connection.send_messages(messages)

        # Update all as sent in bulk
        notifications.update(is_sent=True)
        return f"✅ Successfully sent {len(messages)} email(s)."

    except Exception as e:
        print(f"❌ Failed to send bulk emails: {e}")
        return f"Failed: {e}"
