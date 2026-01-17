from datetime import datetime
from django.utils import timezone


def now():
    return timezone.now()


def send_email_notifications():
    """Triggers the celery task to send queued emails."""
    try:
        from notifications.tasks import bulk_send_email_nofication

        # Try async first (non-blocking)
        try:
            bulk_send_email_nofication.delay()
        except Exception:
            # If async fails (Celery broker unavailable), send synchronously
            bulk_send_email_nofication()
    except Exception:
        # If import fails, emails will be sent by periodic schedule
        pass
