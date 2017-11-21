from django.db.models.signals import pre_delete
from django.dispatch import receiver

from ebagis.data.models import Directory, FileData


@receiver(pre_delete, sender=Directory)
@receiver(pre_delete, sender=FileData)
def create_user_profile(sender, instance, using, **kwargs):
    instance.cleanup()
