from django.core.validators import FileExtensionValidator
from django.db import models

from jobs.models import Job

from .utils import now, resume_upload_path, valid_id_upload_path


def normalize_name_part(value):
    return " ".join((value or "").split()).strip()


class Applicant(models.Model):
    class Meta:
        ordering = ["-id"]
        db_table = "applicants"
        verbose_name_plural = "Applicants"

    def __str__(self):
        return f"{self.full_name}"

    def compose_full_name(self):
        parts = [
            normalize_name_part(self.first_name),
            normalize_name_part(self.middle_name),
            normalize_name_part(self.last_name),
        ]
        return " ".join(part for part in parts if part).strip()

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
        blank=False,
        null=False,
    )
    first_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )
    middle_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )
    last_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )
    email = models.CharField(
        max_length=100,
        blank=False,
        null=False,
    )
    contact_number = models.CharField(
        max_length=100,
        blank=False,
        null=False,
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
    verification_token = models.CharField(
        max_length=60,
        null=True,
        blank=True,
    )
    token_created = models.DateTimeField(
        null=True,
        blank=True,
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

    def save(self, *args, **kwargs):
        update_fields = kwargs.get("update_fields")
        self.first_name = normalize_name_part(self.first_name) or None
        self.middle_name = normalize_name_part(self.middle_name) or None
        self.last_name = normalize_name_part(self.last_name) or None

        # Keep current flows working until serializers/forms are migrated:
        # if split fields exist, they become the source of truth; otherwise keep
        # the submitted full_name as-is after normalization.
        derived_full_name = self.compose_full_name()
        self.full_name = derived_full_name or normalize_name_part(self.full_name)

        if update_fields is not None:
            update_fields = set(update_fields)
            if update_fields.intersection({"first_name", "middle_name", "last_name", "full_name"}):
                update_fields.update({"first_name", "middle_name", "last_name", "full_name"})
                kwargs["update_fields"] = list(update_fields)

        super().save(*args, **kwargs)
