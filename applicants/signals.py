from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Applicant
from notifications.models import EmailNotification
from django.utils.html import escape


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

    EmailNotification.objects.create(
        subject=subject,
        recipient=applicant.email,
        body=body,
        created_by="sys",
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

    EmailNotification.objects.create(
        subject=subject,
        recipient=applicant.email,
        body=body,
        created_by="sys",
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

    EmailNotification.objects.create(
        subject=subject,
        recipient=applicant.email,
        body=body,
        created_by="sys",
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

    EmailNotification.objects.create(
        subject=subject,
        recipient=applicant.email,
        body=body,
        created_by="sys",
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

    EmailNotification.objects.create(
        subject=subject,
        recipient=applicant.email,
        body=body,
        created_by="sys",
    )
