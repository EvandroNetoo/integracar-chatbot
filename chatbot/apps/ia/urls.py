from django.urls import path

from ia import views

urlpatterns = [
    path(
        'chat/',
        views.ChatView.as_view(),
        name='chat',
    ),
    path(
        'documentos/',
        views.DocumentosView.as_view(),
        name='documentos',
    ),
    path(
        'importar-documentos/',
        views.ImportarDocumentosView.as_view(),
        name='importar_documentos',
    ),
]
