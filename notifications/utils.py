from datetime import datetime
from django.utils import timezone


def now():
    return timezone.now()
