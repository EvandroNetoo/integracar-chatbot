from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django_q.tasks import async_task

from ia.models import Documento
from ia.tasks import gerar_embedding_documento


@receiver(pre_save, sender=Documento)
def set_nome_documento(sender: type[Documento], instance: Documento, **kwargs):
    if not instance.nome:
        instance.nome = instance.arquivo.name


@receiver(post_save, sender=Documento)
def create_embedding_documento(
    sender: type[Documento],
    instance: Documento,
    created: bool,
    **kwargs,
):
    if created:
        async_task(gerar_embedding_documento, instance.id)
