from django.db import models
from .utils import now


class EmailNotification(models.Model):
    class Meta:
        ordering = ["-id"]
        db_table = "email_notifications"
        verbose_name_plural = "Email Notifications"

    def __str__(self):
        return f"{self.subject}"

    subject = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )
    recipient = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )
    body = models.TextField(
        blank=True,
        null=True,
    )
    is_sent = models.BooleanField(
        default=False,
        blank=True,
        null=True,
    )
    created_by = models.CharField(
        max_length=10,
        default="sys",
        null=True,
        blank=True,
    )
    date_created = models.DateTimeField(
        default=now,
        null=True,
        blank=True,
    )
