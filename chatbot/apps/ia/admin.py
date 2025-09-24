from django.contrib import admin

from ia.models import Documento, EmbeddingDocumento

admin.site.register(Documento)
admin.site.register(EmbeddingDocumento)
