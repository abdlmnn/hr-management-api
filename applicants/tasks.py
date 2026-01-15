from datetime import timedelta
from django.utils import timezone
from celery import shared_task
from .models import Applicant
from django.core.cache import cache
from .services import verification_token_expiry
from django.utils.html import escape
from django.core.mail import EmailMessage
import os


@shared_task
def cleanup_expired_application():
    # Test delete more than 1 day
    # Default delete more than 7 days
    cutoff = timezone.now() - timedelta(days=1)

    Applicant.objects.filter(status="pending", token_created__lte=cutoff).delete()


verification_email_lock_time = 60 * 5  # prevent deadlocks if workers crashes


@shared_task(bind=True, name="send_single_verification_email")
def send_single_verification_email(self, applicant_id):
    """
    Send a single verification email to an applicant.
    To prevent multiple emails from being sent to the same applicant, we use a lock.
    """
    lock_id = f"verification_email_lock_{applicant_id}"

    print("LOCK ID:", lock_id)

    if not cache.add(lock_id, "locked", verification_email_lock_time):
        print("Task already running for this applicant.")
        return

    try:
        try:
            applicant = Applicant.objects.get(id=applicant_id)
        except Applicant.DoesNotExist:
            print("Applicant not found.")
            return

        verification_url = f"http://127.0.0.1:8000/api/v1/applicants/{applicant.verification_token}/verify/"
        subject = "Verify your Application"
        body = (
            f"Dear {escape(applicant.full_name)},<br><br>"
            "Please verify your application by clicking the link below:<br>"
            f"{verification_url}<br><br>"
            f"This link expires in {verification_token_expiry} minute(s).<br><br>"
            "Best Regards,<br>"
            "ILPI Recruitment Team.<br><br><br><br>"
        )

        email = EmailMessage(
            subject=subject,
            body=body,
            from_email=os.getenv("EMAIL_HOST_USER"),
            to=[applicant.email],
        )
        email.content_subtype = "html"
        email.send()

        print("Email sent successfully.")

    except Exception as e:
        print(f"Failed to send verification email to {applicant.email}.")
        raise self.retry(
            exc=e, countdown=60, max_retries=3
        )  # retry task after 60 seconds, up to 3 times

    finally:
        cache.delete(lock_id)  # release the lock, if errors occur.
