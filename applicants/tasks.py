from datetime import timedelta
from django.utils import timezone
from celery import shared_task
from .models import Applicant
from django.core.cache import cache
from django.utils.html import escape
from django.core.mail import EmailMessage
import os
from src.utils import email_notification_body
from .services import generate_applicant_status_report
from .utils import format_report_as_html


verification_token_expiry = 1440  # 24 hours


@shared_task
def cleanup_expired_application():
    """
    Deletes pending applications that are older than 24 hours.
    This task is scheduled to run periodically.
    """
    cutoff = timezone.now() - timedelta(hours=24)
    Applicant.objects.filter(status="pending", date_applied__lte=cutoff).delete()
    print("Cleanup of expired applications completed.")


verification_email_lock_time = 60 * 5  # 5 minutes, prevent deadlocks if workers crashes


@shared_task(bind=True, name="send_single_verification_email")
def send_single_verification_email(self, applicant_id):
    """
    Send a single verification email to an applicant.
    To prevent multiple emails from being sent to the same applicant, we use a Redis lock.
    """
    lock_id = f"verification_email_lock_{applicant_id}"

    if not cache.add(lock_id, "locked", verification_email_lock_time):
        print(f"Lock already exists for applicant {applicant_id}.")
        return

    try:
        try:
            applicant = Applicant.objects.get(pk=applicant_id)
        except Applicant.DoesNotExist:
            return

        base_url = os.environ.get("API_BASE_URL", "http://127.0.0.1:8000")
        verification_url = (
            f"{base_url}/api/v1/applicants/{applicant.verification_token}/verify/"
        )
        subject = "Verify your Application"
        body = (
            f"Dear {escape(applicant.full_name)},<br><br>"
            "Please verify your application by clicking the link below:<br><br>"
            f'<a href="{verification_url}">Verify Application</a><br><br>'
            f"This link expires in 24 hours.<br><br>"
            "Best Regards,<br>"
            "ILPI Recruitment Team.<br><br><br><br>"
        )

        html_content = email_notification_body(email_body=body)

        email = EmailMessage(
            subject=subject,
            body=html_content,
            from_email=os.getenv("EMAIL_HOST_USER"),
            to=[applicant.email],
        )
        email.content_subtype = "html"

        try:
            email.send()
            print(f" Verification email sent to {applicant.email}")
        except Exception as e:
            raise self.retry(
                exc=e, countdown=60, max_retries=3
            )  # retry task after 60 seconds, up to 3 times

    finally:
        cache.delete(lock_id)  # release the lock


@shared_task(name="send_hr_report_email")
def send_hr_report_email():
    """
    Generates and emails a daily report of applicant statuses to HR.
    """
    report_data, period_name = generate_applicant_status_report()

    if report_data is None:
        print("Could not generate HR report data.")
        return

    report_html = format_report_as_html(report_data, period_name)

    subject = f"Applicant Status Report: {period_name}"
    body = (
        "Dear HR Team,<br><br>"
        "Please find below the daily applicant status report.<br><br>"
        f"{report_html}"
        "<br>Best Regards,<br>"
        "ILPI Recruitment System."
    )

    html_content = email_notification_body(email_body=body)

    hr_email = os.environ.get("EMAIL_HOST_USER")

    email = EmailMessage(
        subject=subject,
        body=html_content,
        from_email=hr_email,
        to=[hr_email],
    )
    email.content_subtype = "html"

    try:
        email.send()
        print(f"Daily report sent to {hr_email}")
    except Exception as e:
        print(f"Failed to send daily report to {hr_email}.")
