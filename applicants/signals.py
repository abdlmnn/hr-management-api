from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Applicant
from notifications.models import EmailNotification
from django.utils.html import escape
import os
from django.core.mail import send_mail
from src.utils import email_notification_body

@receiver(pre_save, sender=Applicant)
def applicant_status_change(sender, instance, **kwargs):
    """
    Triggered before saving an Applicant.
    Detects when status changes and runs custom logic.
    """
    if not instance.pk:
        if instance.status == "applied":
            handle_applied(instance)
        return

    try:
        old_instance = Applicant.objects.get(pk=instance.pk)
    except Applicant.DoesNotExist:
        return

    if old_instance.status != instance.status:
        if instance.status == "shortlisted":
            handle_shortlisted(instance)
        elif instance.status == "interview":
            handle_interview(instance)
        elif instance.status == "offered":
            handle_offered(instance)
        elif instance.status == "hired":
            handle_hired(instance)
        elif instance.status == "rejected":
            handle_rejected(instance)


def handle_applied(applicant):
    """
    Called when an applicant applied.
    Creates an Email Notification entry.
    """
    subject = f"Job Application Received"
    body = (
        f"Dear {escape(applicant.full_name)},<br><br>"
        "Thank you for applying for this position. "
        "Our HR team will reach out to you soon with further details.<br><br>"
        "Best Regards,<br>"
        "ILPI Recruitment Team.<br><br><br><br>"
    )

    html_body = email_notification_body(body)

    EmailNotification.objects.create(
        subject=subject,
        recipient=applicant.email,
        body=body,
        created_by="sys",
    )

    # Since celery is not working, send email directly without using tasks.py in notifications
    send_mail(
        subject,
        body,
        os.getenv("EMAIL_HOST_USER"),
        [applicant.email],
        html_message=html_body,
    )

    """
    HR notification for new application
    """
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

    hr_html = email_notification_body(hr_body)

    EmailNotification.objects.create(
        subject=hr_subject,
        recipient=os.environ.get("EMAIL_HOST_USER"),
        body=hr_body,
        created_by="system",
    )

    send_mail(
        hr_subject,
        hr_body,
        os.getenv("EMAIL_HOST_USER"),
        [os.getenv("EMAIL_HOST_USER")],
        html_message=hr_html,
    )



def handle_shortlisted(applicant):
    """
    Called when an applicant is shortlisted.
    Creates an Email Notification entry.
    """
    subject = f"Job Application Shortlisted"
    body = (
        f"Dear {escape(applicant.full_name)},<br><br>"
        "Congratulations! You have been shortlisted for the next phase of the recruitment process. "
        "Our HR team will reach out to you soon with further details.<br><br>"
        "Best Regards,<br>"
        "ILPI Recruitment Team.<br><br><br><br>"
    )

    html_body = email_notification_body(body)

    EmailNotification.objects.create(
        subject=subject,
        recipient=applicant.email,
        body=body,
        created_by="sys",
    )

    # Since celery is not working, send email directly without using tasks.py in notifications
    send_mail(
        subject,
        body,
        os.getenv("EMAIL_HOST_USER"),
        [applicant.email],
        html_message=html_body,
    )


def handle_interview(applicant):
    """
    Called when an applicant is for interview.
    Creates an Email Notification entry.
    """
    subject = f"Job Application Interview"
    body = (
        f"Dear {escape(applicant.full_name)},<br><br>"
        "You are scheduled for an interview. "
        "Our HR team will reach out to you soon with further details.<br><br>"
        "Best Regards,<br>"
        "ILPI Recruitment Team.<br><br><br><br>"
    )

    html_body = email_notification_body(body)

    EmailNotification.objects.create(
        subject=subject,
        recipient=applicant.email,
        body=body,
        created_by="sys",
    )

    # Since celery is not working, send email directly without using tasks.py in notifications
    send_mail(
        subject,
        body,
        os.getenv("EMAIL_HOST_USER"),
        [applicant.email],
        html_message=html_body,
    )


def handle_offered(applicant):
    pass


def handle_hired(applicant):
    """
    Called when an applicant is hired.
    Creates an Email Notification entry.
    """
    subject = f"Job Application Status"
    body = (
        f"Dear {escape(applicant.full_name)},<br><br>"
        "You are HIRED!. Welcome to the ILPI Family. "
        "Our HR team will reach out to you soon with further details.<br><br>"
        "Best Regards,<br>"
        "ILPI Recruitment Team.<br><br><br><br>"
    )

    html_body = email_notification_body(body)

    EmailNotification.objects.create(
        subject=subject,
        recipient=applicant.email,
        body=body,
        created_by="sys",
    )

    # Since celery is not working, send email directly without using tasks.py in notifications
    send_mail(
        subject,
        body,
        os.getenv("EMAIL_HOST_USER"),
        [applicant.email],
        html_message=html_body,
    )


def handle_rejected(applicant):
    """
    Called when an applicant is rejected.
    Creates an Email Notification entry.
    """
    subject = f"Job Application Status"
    body = (
        f"Dear {escape(applicant.full_name)},<br><br>"
        "We are sorry to inform you that you did not made the cut. "
        "But thank you for applying.<br><br>"
        "Best Regards,<br>"
        "ILPI Recruitment Team.<br><br><br><br>"
    )

    html_body = email_notification_body(body)

    EmailNotification.objects.create(
        subject=subject,
        recipient=applicant.email,
        body=body,
        created_by="sys",
    )

    # Since celery is not working, send email directly without using tasks.py in notifications
    send_mail(
        subject,
        body,
        os.getenv("EMAIL_HOST_USER"),
        [applicant.email],
        html_message=html_body,
    )
