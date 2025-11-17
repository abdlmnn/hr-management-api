from django.db import models
from .utils import now


class JobType(models.Model):
    class Meta:
        ordering = ["-id"]
        db_table = "job_types"
        verbose_name_plural = "Job Types"

    def __str__(self):
        return f"{self.name}"

    name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )
    code = models.CharField(
        max_length=100,
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
