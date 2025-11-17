from datetime import datetime
import os
from django.utils import timezone


def now():
    return timezone.now()
    # return datetime.now()


def valid_id_upload_path(instance, filename):
    """
    Store valid_id as: applicants/<applicant_name>/<applicant_name>_valid_id.pdf
    """
    safe_name = (
        instance.full_name.replace(" ", "_") if instance.full_name else "unknown"
    )
    return f"applicants/{safe_name}/{safe_name}_valid_id.pdf"


def resume_upload_path(instance, filename):
    """
    Store resume as: applicants/<applicant_name>/<applicant_name>_resume.pdf
    """
    safe_name = (
        instance.full_name.replace(" ", "_") if instance.full_name else "unknown"
    )
    return f"applicants/{safe_name}/{safe_name}_resume.pdf"
