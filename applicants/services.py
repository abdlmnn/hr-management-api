from django.utils import timezone
from rest_framework.exceptions import ValidationError, NotFound
from .models import Applicant
from notifications.models import EmailNotification
from .utils import generate_verification_token
from datetime import timedelta, date
import os
from django.utils.html import escape
from django.db.models import Count
from email_templates.models import EmailTemplate


def create_application(data, username):
    """
    Creates or updates an applicant.
    - If applicant with 'pending' status exists, resend verification.
    - If a recent, non-pending application exists, block it.
    - Otherwise, create a new applicant.
    """
    email = data.get("email")
    job = data.get("job")

    time_threshold = timezone.now() - timedelta(hours=24)
    if (
        Applicant.objects.filter(
            email__iexact=email, job=job, date_applied__gte=time_threshold
        )
        .exclude(status="pending")
        .exists()
    ):
        raise ValidationError(
            "You have already applied for this job. Please wait 24 hours before applying again."
        )

    applicant = Applicant.objects.filter(
        email__iexact=email, job=job, status="pending"
    ).first()

    token = generate_verification_token()

    if applicant:

        if applicant.token_created and (
            timezone.now() - applicant.token_created < timedelta(minutes=15)
        ):
            raise ValidationError(
                "A verification email has recently been sent. Please check your inbox (and spam folder)."
            )

    else:
        applicant = Applicant.objects.create(
            **data,
            verification_token=token,
            token_created=timezone.now(),
            updated_by=username,
        )

    from .tasks import send_single_verification_email

    task_id = f"verification-email-for-applicant-{applicant.id}"
    send_single_verification_email.apply_async(
        args=[applicant.id],
        task_id=task_id,
        time_limit=300,  # 5 minutes
        soft_time_limit=240,  # 4 minutes
    )

    return applicant


def send_applicant_status_notification(applicant_id):
    """
    Manually sends a notification to an applicant based on their current status.
    """
    try:
        applicant = Applicant.objects.get(pk=applicant_id)
    except Applicant.DoesNotExist:
        raise NotFound(f"Applicant with ID {applicant_id} not found.")

    status_handler_map = {
        "applied": handle_applied,
        "shortlisted": handle_shortlisted,
        "interview": handle_interview,
        "offered": handle_offered,
        "hired": handle_hired,
        "rejected": handle_rejected,
    }

    handler = status_handler_map.get(applicant.status)

    if handler:
        handler(applicant)
        return True
    else:
        return False


def create_and_send_email(applicant, status):
    """
    Helper function to create and send email notifications.
    """
    try:
        template = EmailTemplate.objects.get(status=status)
        subject = template.subject.format(
            job_name=applicant.job.name if applicant.job else "Position"
        )
        body = template.body.format(applicant_full_name=escape(applicant.full_name))
    except EmailTemplate.DoesNotExist:
        subject = f"Job Application {status.title()}"
        body = (
            f"Dear {escape(applicant.full_name)},<br><br>"
            f"Your application status has been updated to {status}.<br><br>"
            "Best Regards,<br>"
            "ILPI Recruitment Team.<br><br><br><br>"
        )

    EmailNotification.objects.create(
        subject=subject,
        recipient=applicant.email,
        body=body,
        created_by="sys",
    )


def handle_applied(applicant):
    """
    Creates email notifications for 'applied' status.
    """
    create_and_send_email(applicant, "applied")

    hr_subject = f"New Job Application Received: {applicant.job.name if applicant.job else 'Position not specified'}"
    hr_body = (
        f"Dear HR Team,<br><br>"
        f"A new job application has been received for the position of {applicant.job.name if applicant.job else 'Position not specified'}.<br><br>"
        f"Applicant Name: {escape(applicant.full_name)}<br>"
        f"Email: {escape(applicant.email)}<br>"
        f"Phone: {escape(applicant.contact_number)}<br><br>"
        "Please review the application at your earliest convenience.<br><br>"
        "Best Regards,<br>"
        "ILPI Recruitment System.<br><br><br><br>"
    )

    EmailNotification.objects.create(
        subject=hr_subject,
        recipient=os.environ.get("EMAIL_HOST_USER"),
        body=hr_body,
        created_by="system",
    )


def handle_shortlisted(applicant):
    """
    Creates an Email Notification for 'shortlisted' status.
    """
    create_and_send_email(applicant, "shortlisted")


def handle_interview(applicant):
    """
    Creates an Email Notification for 'interview' status.
    """
    create_and_send_email(applicant, "interview")


def handle_offered(applicant):
    """
    Creates an Email Notification for 'offered' status.
    """
    create_and_send_email(applicant, "offered")


def handle_hired(applicant):
    """
    Creates an Email Notification for 'hired' status.
    """
    create_and_send_email(applicant, "hired")


def handle_rejected(applicant):
    """
    Creates an Email Notification for 'rejected' status.
    """
    create_and_send_email(applicant, "rejected")


def generate_applicant_status_report():
    """
    Generates a report of applicant counts by status for the last 24 hours.
    """
    today = date.today()
    start_date = today - timedelta(days=1)
    period_name = "Last 24 hours"

    report_data = (
        Applicant.objects.filter(date_applied__gte=start_date)
        .values("status")
        .annotate(count=Count("status"))
        .order_by("-count")
    )

    # Dictionary for easier lookup
    status_counts = {item["status"]: item["count"] for item in report_data}

    # All statuses are present in the report
    all_statuses = [status[0] for status in Applicant.STATUS_CHOICES]
    full_report = {status: status_counts.get(status, 0) for status in all_statuses}

    return full_report, period_name
