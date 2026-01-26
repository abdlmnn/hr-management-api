from django.db import models


class EmailTemplate(models.Model):
    name = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    body = models.TextField()
    # Status is optional to support custom templates not bound to a specific applicant status.
    # When provided, it must be unique (unique=True) so a single default template exists per status.
    status = models.CharField(max_length=255, unique=True, null=True, blank=True)

    def __str__(self):
        return self.name