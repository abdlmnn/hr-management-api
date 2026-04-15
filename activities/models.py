from django.db import models

from .utils import now


class Activity(models.Model):
    class Meta:
        ordering = ["-id"]
        db_table = "activities"
        verbose_name_plural = "Activities"

    def __str__(self):
        if self.when_end:
            return f"{self.what} @ {self.when} – {self.when_end}"
        return f"{self.what} @ {self.when}"

    what = models.CharField(max_length=200, blank=False, null=False)
    where = models.CharField(max_length=300, blank=False, null=False)
    when = models.DateTimeField(blank=False, null=False)
    when_end = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Optional end time for multi-day activities.",
    )
    note = models.TextField(
        blank=True,
        null=True,
        help_text="Optional notes or extra context for this activity.",
    )

    created_by = models.CharField(max_length=10, default="sys", null=True, blank=True)
    updated_by = models.CharField(max_length=10, default="sys", null=True, blank=True)
    date_created = models.DateTimeField(default=now, null=True, blank=True)

