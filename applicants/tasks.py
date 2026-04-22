from datetime import timedelta
from django.utils import timezone
from celery import shared_task
from .models import Applicant
import os
from .services import generate_applicant_status_report
from .utils import format_report_as_html
from src.utils import email_notification_body
from django.core.mail import EmailMessage


@shared_task
def cleanup_expired_application():
    """
    Deletes pending applications that are older than 24 hours.
    This task is scheduled to run periodically.
    """
    cutoff = timezone.now() - timedelta(hours=24)
    Applicant.objects.filter(status="pending", date_applied__lte=cutoff).delete()
    print("Cleanup of expired applications completed.")


@shared_task(name="applicants.tasks.send_hr_report_email")
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
