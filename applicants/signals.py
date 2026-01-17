from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Applicant
from applicants.services import handle_applied


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
