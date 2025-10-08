from __future__ import annotations

from django.core.validators import FileExtensionValidator
from django.db import models
from django.db.models import Field
from django.db.models.lookups import PostgresOperatorLookup
from pgvector.django import VectorField

from ia.indexes import BM25Index


@Field.register_lookup
class BM25(PostgresOperatorLookup):
    lookup_name = 'bm25'
    postgres_operator = '@@@'


class DocumentoStatusChoices(models.TextChoices):
    PENDENTE = 'pendente', 'Pendente'
    PROCESSANDO = 'processando', 'Processando'
    PROCESSADO = 'processado', 'Processado'


class Documento(models.Model):
    nome = models.CharField(max_length=255, blank=True)
    arquivo = models.FileField(
        upload_to='documentos/',
        validators=[FileExtensionValidator(['pdf'])],
    )
    conteudo = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=DocumentoStatusChoices.choices,
        default=DocumentoStatusChoices.PENDENTE,
    )

    criado_em = models.DateTimeField(auto_now_add=True)

    embeddings: models.QuerySet[ChunkDocumeto]

    def __str__(self):
        return self.nome


class ChunkDocumeto(models.Model):
    documento = models.ForeignKey(
        Documento, on_delete=models.CASCADE, related_name='embeddings'
    )
    conteudo = models.TextField()
    embedding = VectorField(dimensions=1024)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            BM25Index(
                fields=['id', 'conteudo'],
                key_field='id',
                name='bm25_index_conteudo',
            ),
        ]

    def __str__(self):
        return self.conteudo[:50]
