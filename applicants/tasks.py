from datetime import timedelta
from django.utils import timezone
from celery import shared_task
from .models import Applicant


@shared_task
def cleanup_expired_application():
    # Test delete more than 1 day
    # Default delete more than 7 days
    cutoff = timezone.now() - timedelta(days=1)

    Applicant.objects.filter(status="pending", token_created__lte=cutoff).delete()
