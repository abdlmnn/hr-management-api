from django.db import models
from .utils import now, valid_id_upload_path, resume_upload_path
from jobs.models import Job
from django.core.validators import FileExtensionValidator


class Applicant(models.Model):
    class Meta:
        ordering = ["-id"]
        db_table = "applicants"
        verbose_name_plural = "Applicants"

    def __str__(self):
        return f"{self.full_name}"

    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("applied", "Applied"),
        ("shortlisted", "Shortlisted"),
        ("interview", "Interview"),
        ("offered", "Offered"),
        ("hired", "Hired"),
        ("rejected", "Rejected"),
    )

    full_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )
    email = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )
    contact_number = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )
    job = models.ForeignKey(
        Job,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="applicants",
    )
    cover_letter = models.TextField(
        blank=True,
        null=True,
    )
    valid_id = models.FileField(
        upload_to=valid_id_upload_path,
        validators=[FileExtensionValidator(allowed_extensions=["pdf"])],
        blank=True,
        null=True,
    )
    resume = models.FileField(
        upload_to=resume_upload_path,
        validators=[FileExtensionValidator(allowed_extensions=["pdf"])],
        blank=True,
        null=True,
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
        null=False,
        blank=False,
    )
    updated_by = models.CharField(
        max_length=10,
        default="sys",
        null=True,
        blank=True,
    )
    date_applied = models.DateTimeField(
        default=now,
        null=False,
        blank=False,
    )
