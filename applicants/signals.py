from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from applicants.services import handle_applied
from employees.services import sync_employee_from_applicant

from .models import Applicant


@receiver(pre_save, sender=Applicant)
def applicant_status_change(sender, instance, **kwargs):
    """
    Triggered before saving an Applicant.
    Detects when status changes to 'applied' and triggers a notification
    by calling the centralized handler in the services layer.
    """
    if not instance.pk:
        return

    try:
        old_instance = Applicant.objects.get(pk=instance.pk)

        if old_instance.status != "applied" and instance.status == "applied":
            handle_applied(instance)

    except Applicant.DoesNotExist:
        return


@receiver(post_save, sender=Applicant)
def applicant_hired_sync_employee(sender, instance, created, **kwargs):
    if created and instance.status != "hired":
        return

    sync_employee_from_applicant(instance, username=instance.updated_by or "sys")
