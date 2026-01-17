from django.db import models


class EmailTemplate(models.Model):
    name = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    body = models.TextField()
    status = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name