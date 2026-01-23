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
    notification_list = list(notifications)
    for n in notification_list:
        html_content = email_notification_body(email_body=n.body)
        msg = EmailMessage(
            subject=n.subject,
            body=html_content,
            from_email=os.getenv("EMAIL_HOST_USER"),
            to=[n.recipient],
        )
        msg.content_subtype = "html"
        messages.append((msg, n))

    # Send all emails in one SMTP session
    try:
        with get_connection() as connection:
            connection.send_messages([msg for msg, _ in messages])

        # Update all as sent in bulk
        notifications.update(is_sent=True, error_message=None, last_attempt=timezone.now())
        return f"✅ Successfully sent {len(messages)} email(s)."

    except Exception as e:
        error_str = str(e)
        print(f"❌ Failed to send bulk emails: {error_str}")
        
        # Try to send individually to track which ones failed
        success_count = 0
        failed_count = 0
        
        for msg, notification in messages:
            try:
                with get_connection() as connection:
                    connection.send_messages([msg])
                # Mark as sent
                notification.is_sent = True
                notification.error_message = None
                notification.last_attempt = timezone.now()
                notification.save()
                success_count += 1
            except Exception as individual_error:
                # Track individual failure
                notification.is_sent = False
                notification.error_message = str(individual_error)
                notification.retry_count += 1
                notification.last_attempt = timezone.now()
                notification.save()
                failed_count += 1
        
        return f"⚠️ Partial success: {success_count} sent, {failed_count} failed. Error: {error_str}"
