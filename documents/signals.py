from django.db.models.signals import pre_delete
from django.dispatch import receiver

from .models import Document
from .utils import delete_document_chunks


@receiver(pre_delete, sender=Document)
def remove_document_from_chroma(sender, instance, **kwargs):
    delete_document_chunks(instance.id)