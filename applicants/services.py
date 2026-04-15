from django.utils import timezone
from rest_framework.exceptions import ValidationError, NotFound
from .models import Applicant
from notifications.models import EmailNotification
from .utils import generate_verification_token, format_plain_text_to_html
from datetime import timedelta, date
import os
from django.utils.html import escape
from django.db.models import Count
from email_templates.models import EmailTemplate


def _get_applicant_job_name(applicant):
    if applicant.job and applicant.job.name:
        return applicant.job.name
    return "Position not specified"


def _get_applicant_status_label(applicant):
    return dict(Applicant.STATUS_CHOICES).get(
        applicant.status, applicant.status.title()
    )


def _format_applicant_email_text(value, applicant, escape_html=False):
    if not value:
        return ""

    applicant_name = applicant.full_name or "Applicant"
    job_name = _get_applicant_job_name(applicant)

    replacements = {
        "{applicant_full_name}": (
            escape(applicant_name) if escape_html else applicant_name
        ),
        "{job_name}": escape(job_name) if escape_html else job_name,
    }

    formatted = value
    for placeholder, replacement in replacements.items():
        formatted = formatted.replace(placeholder, replacement)

    return formatted


def _build_application_summary_html(applicant):
    return (
        "<br><br>"
        "Please find below a summary of your job application for your reference:<br><br>"
        f"Position Applied For: {escape(_get_applicant_job_name(applicant))}<br>"
        f"Current Application Status: {escape(_get_applicant_status_label(applicant))}<br>"
        f"Applicant Name: {escape(applicant.full_name or 'Applicant')}<br><br>"
        "We appreciate your continued interest in pursuing employment with ILPI. "
        "Should you require any clarification, our Human Resources team will be pleased to assist you.<br><br>"
    )


def _append_application_summary(body, applicant):
    return f"{body}{_build_application_summary_html(applicant)}"


def _build_hr_application_summary_html(applicant):
    submitted_at = (
        timezone.localtime(applicant.date_applied).strftime("%B %d, %Y %I:%M %p")
        if applicant.date_applied
        else "Not available"
    )
    cover_letter = escape(applicant.cover_letter) if applicant.cover_letter else "Not provided"

    return (
        "Applicant details are as follows:<br><br>"
        f"Position Applied For: {escape(_get_applicant_job_name(applicant))}<br>"
        f"Application Status: {escape(_get_applicant_status_label(applicant))}<br>"
        f"Applicant Name: {escape(applicant.full_name or 'Applicant')}<br>"
        f"Email Address: {escape(applicant.email or 'Not provided')}<br>"
        f"Contact Number: {escape(applicant.contact_number or 'Not provided')}<br>"
        f"Date Submitted: {escape(submitted_at)}<br>"
        f"Cover Letter: {cover_letter}<br><br>"
    )


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

    # Always generate a fresh token for create/resend paths (saved below)
    token = generate_verification_token()
    now = timezone.now()

    if applicant:
        # Anti-spam: don't resend too frequently
        if applicant.token_created and (
            now - applicant.token_created < timedelta(minutes=15)
        ):
            raise ValidationError(
                "A verification email has recently been sent. Please check your inbox (and spam folder)."
            )

        # Update applicant details with latest submission (optional but helpful for corrections)
        # Keep status as pending until verified.
        applicant.full_name = data.get("full_name", applicant.full_name)
        applicant.contact_number = data.get("contact_number", applicant.contact_number)
        applicant.cover_letter = data.get("cover_letter", applicant.cover_letter)
        if data.get("valid_id") is not None:
            applicant.valid_id = data.get("valid_id")
        if data.get("resume") is not None:
            applicant.resume = data.get("resume")

        # Rotate verification token and timestamp so resend link is always valid/fresh
        applicant.verification_token = token
        applicant.token_created = now
        applicant.updated_by = username
        applicant.save(
            update_fields=[
                "full_name",
                "contact_number",
                "cover_letter",
                "valid_id",
                "resume",
                "verification_token",
                "token_created",
                "updated_by",
            ]
        )
    else:
        applicant = Applicant.objects.create(
            **data,
            verification_token=token,
            token_created=now,
            updated_by=username,
        )

    base_url = os.environ.get("API_BASE_URL", "http://127.0.0.1:8000")
    verification_url = (
        f"{base_url}/api/v1/applicants/{applicant.verification_token}/verify/"
    )
    subject = "Verify your Application"
    body = (
        f"Dear {escape(applicant.full_name)},<br><br>"
        "Thank you for your interest in employment opportunities with ILPI.<br><br>"
        "Please verify your application by clicking the link below:<br><br>"
        f'<a href="{verification_url}">Verify Application</a><br><br>'
        "For your reference, your application details are summarized below:<br><br>"
        f"Position Applied For: {escape(_get_applicant_job_name(applicant))}<br>"
        f"Current Application Status: {escape(_get_applicant_status_label(applicant))}<br>"
        f"Applicant Name: {escape(applicant.full_name or 'Applicant')}<br><br>"
        "Kindly note that this verification link will expire in 24 hours.<br><br>"
        "Best Regards,<br>"
        "ILPI Recruitment Team.<br><br><br><br>"
    )

    EmailNotification.objects.create(
        subject=subject,
        recipient=applicant.email,
        body=body,
        created_by=username,
    )

    return applicant


def send_applicant_status_notification(applicant_id, subject=None, body=None):
    """
    Manually sends a notification to an applicant based on their current status.
    Accepts optional 'subject' and 'body' to override template values.

    The 'body' parameter accepts plain text from HR users and automatically
    formats it to HTML for email delivery. Template variables (e.g., {applicant_full_name})
    are preserved and will be formatted later.
    """
    try:
        applicant = Applicant.objects.get(pk=applicant_id)
    except Applicant.DoesNotExist:
        raise NotFound(f"Applicant with ID {applicant_id} not found.")

    # If custom subject/body provided, create email directly without using template
    if subject and body:
        # Format plain text body to HTML (converts newlines to <br>, escapes HTML, preserves template variables)
        formatted_subject = _format_applicant_email_text(subject, applicant)
        formatted_body = format_plain_text_to_html(
            _format_applicant_email_text(body, applicant)
        )
        formatted_body = _append_application_summary(formatted_body, applicant)

        EmailNotification.objects.create(
            subject=formatted_subject,
            recipient=applicant.email,
            body=formatted_body,
            created_by="sys",
        )
        return True

    # Otherwise, use template-based flow
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
        subject = _format_applicant_email_text(template.subject, applicant)
        body = _format_applicant_email_text(
            template.body, applicant, escape_html=True
        )
    except EmailTemplate.DoesNotExist:
        status_label = _get_applicant_status_label(applicant)
        position_name = escape(_get_applicant_job_name(applicant))
        subject = f"Application Update for {_get_applicant_job_name(applicant)}"
        body = (
            f"Dear {escape(applicant.full_name)},<br><br>"
            "We are writing to provide an update regarding your application.<br><br>"
            f"Your application for the {position_name} position is currently under the "
            f'"{escape(status_label)}" status.<br><br>'
            "Best Regards,<br>"
            "ILPI Recruitment Team.<br><br><br><br>"
        )

    body = _append_application_summary(body, applicant)

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
        "A new job application has been successfully verified and is now ready for review.<br><br>"
        f"{_build_hr_application_summary_html(applicant)}"
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
