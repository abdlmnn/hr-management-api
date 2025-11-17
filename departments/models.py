from django.db import models
from .utils import now


class Department(models.Model):
    class Meta:
        ordering = ["-id"]
        db_table = "departments"
        verbose_name_plural = "Departments"

    def __str__(self):
        return f"{self.name}"

    name = models.TextField(
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
