from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django_q.tasks import Chain

from ia.models import Documento
from ia.rag import Rag


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
    if not instance.conteudo:
        chain = Chain()
        chain.append(Rag.extrair_e_salvar_conteudo, id_documento=instance.id)
        chain.append(Rag.gerar_e_embedar_chunks, id_documento=instance.id)
        chain.run()
